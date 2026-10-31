from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from populate_core.models import AccessPolicy
from users.models import Role
from assets.models import (
    AssetCategory,
    AssetVendor,
    AssetPurchase,
    Asset,
    AssetAllocation,
    AssetIncident,
    AssetRepair,
    AssetStockLedger
)

User = get_user_model()


class AssetLifecycleTestCase(TestCase):
    def setUp(self):
        self.role_admin, _ = Role.objects.get_or_create(name="IT Admin", defaults={"is_superadmin": True})
        self.role_emp, _ = Role.objects.get_or_create(name="Employee", defaults={"is_superadmin": False})

        for model_name in [
            "asset_category",
            "asset_vendor",
            "asset_purchase",
            "asset",
            "asset_allocation",
            "asset_incident",
            "asset_repair",
            "asset_stock_ledger"
        ]:
            AccessPolicy.objects.get_or_create(
                role=self.role_emp,
                model_name=model_name,
                defaults={
                    "actions": ["read", "create", "update", "delete"],
                    "allow_access": {"read": ["*"], "create": ["*"], "update": ["*"], "delete": ["*"]},
                    "status": 1
                }
            )

        self.admin = User.objects.create_user(username="admin_it", email="admin_it@example.com", is_superuser=True)
        self.alice = User.objects.create_user(username="alice_dev", email="alice@example.com", role=self.role_emp)
        self.bob = User.objects.create_user(username="bob_qa", email="bob@example.com", role=self.role_emp)

        self.client = APIClient()

    def test_complete_asset_management_lifecycle(self):
        # ----------------------------------------------------
        # 1. Master Setup: Category & Vendor (Short code defined by user)
        # ----------------------------------------------------
        self.client.force_authenticate(user=self.admin)

        # Missing code rejected
        res_cat_err = self.client.post("/api/populate/create/asset_category/", {"name": "Laptops"}, format="json")
        self.assertIn(res_cat_err.status_code, (400, 500))

        # Valid Category with user-defined code "LAP"
        res_cat_lap = self.client.post("/api/populate/create/asset_category/", {"name": "Laptops", "code": "lap"}, format="json")
        self.assertEqual(res_cat_lap.status_code, 201)
        cat_lap = AssetCategory.objects.get(name="Laptops")
        self.assertEqual(cat_lap.code, "LAP")

        # Category for Monitors with code "MON"
        res_cat_mon = self.client.post("/api/populate/create/asset_category/", {"name": "Monitors", "code": "mon"}, format="json")
        self.assertEqual(res_cat_mon.status_code, 201)
        cat_mon = AssetCategory.objects.get(name="Monitors")
        self.assertEqual(cat_mon.code, "MON")

        # Create Vendor
        res_vendor = self.client.post("/api/populate/create/asset_vendor/", {
            "name": "Dell Enterprise Solutions",
            "contact_person": "Michael Scott",
            "phone": "+18005550199",
            "gstin": "29AAAAA0000A1Z5"
        }, format="json")
        self.assertEqual(res_vendor.status_code, 201, res_vendor.data)
        vendor = AssetVendor.objects.get(name="Dell Enterprise Solutions")

        # ----------------------------------------------------
        # 2. Direct Asset Creation with Dynamic Category Code
        # ----------------------------------------------------
        res_asset = self.client.post("/api/populate/create/asset/", {
            "category": cat_lap.id,
            "name": "Dell XPS 15",
            "make": "Dell",
            "model": "XPS 9520",
            "serial_number": "SN-XPS-9520-001"
        }, format="json")
        self.assertEqual(res_asset.status_code, 201)
        asset_item = res_asset.data["data"]
        asset_id_pk = asset_item[0]["id"] if isinstance(asset_item, list) else asset_item["id"]
        xps_asset = Asset.objects.get(id=asset_id_pk)
        
        # Verify dynamic code derivation: starts with "LAP-"
        self.assertTrue(xps_asset.asset_id.startswith("LAP-"))
        self.assertEqual(xps_asset.asset_status, "Available")
        self.assertEqual(xps_asset.condition, "Good")

        # Verify initial registration stock ledger entry
        initial_ledger = AssetStockLedger.objects.filter(asset=xps_asset, transaction_type="IN").first()
        self.assertIsNotNone(initial_ledger)
        self.assertEqual(initial_ledger.trigger_type, "Purchase_Receipt")

        # ----------------------------------------------------
        # 3. Procurement PO & Automated GRN Goods Receipt
        # ----------------------------------------------------
        res_po = self.client.post("/api/populate/create/asset_purchase/", {
            "vendor": vendor.id,
            "items": [
                {"category_id": cat_mon.id, "name": "Dell UltraSharp 27", "model": "U2723QE", "quantity": 2, "unit_price": 450.00}
            ],
            "paid_amount": 900.00
        }, format="json")
        self.assertEqual(res_po.status_code, 201)
        po_item = res_po.data["data"]
        po_id = po_item[0]["id"] if isinstance(po_item, list) else po_item["id"]
        po = AssetPurchase.objects.get(id=po_id)
        self.assertEqual(po.payment_status, "Paid")
        self.assertEqual(po.purchase_status, "Draft")

        # Mark PO as Received -> Triggers GRN asset generation
        res_rcv = self.client.post(f"/api/populate/update/asset_purchase/{po_id}/", {
            "purchase_status": "Received"
        }, format="json")
        self.assertEqual(res_rcv.status_code, 200)
        po.refresh_from_db()
        self.assertEqual(po.purchase_status, "Received")

        # Verify 2 Monitor assets auto-generated with "MON-" prefix
        gen_monitors = Asset.objects.filter(purchase=po)
        self.assertEqual(gen_monitors.count(), 2)
        for m in gen_monitors:
            self.assertTrue(m.asset_id.startswith("MON-"))
            self.assertEqual(m.asset_status, "Available")
            self.assertTrue(AssetStockLedger.objects.filter(asset=m, trigger_type="Purchase_Receipt").exists())

        # ----------------------------------------------------
        # 4. Asset Allocation Workflow & Duplicate Guard
        # ----------------------------------------------------
        self.client.force_authenticate(user=self.alice)

        # Alice requests Dell XPS laptop allocation
        res_alloc = self.client.post("/api/populate/create/asset_allocation/", {
            "asset": xps_asset.id,
            "employee": self.alice.id,
            "allocation_type": "Allocation"
        }, format="json")
        self.assertEqual(res_alloc.status_code, 201)
        alloc_item = res_alloc.data["data"]
        alloc_id = alloc_item[0]["id"] if isinstance(alloc_item, list) else alloc_item["id"]
        
        # Verify asset is reserved
        xps_asset.refresh_from_db()
        self.assertEqual(xps_asset.asset_status, "Reserved")

        # Bob attempts duplicate allocation on the reserved asset -> rejected
        self.client.force_authenticate(user=self.bob)
        res_dup_alloc = self.client.post("/api/populate/create/asset_allocation/", {
            "asset": xps_asset.id,
            "employee": self.bob.id,
            "allocation_type": "Allocation"
        }, format="json")
        self.assertIn(res_dup_alloc.status_code, (400, 403, 500))

        # Admin approves allocation -> Active
        self.client.force_authenticate(user=self.admin)
        res_approve = self.client.post(f"/api/populate/update/asset_allocation/{alloc_id}/", {
            "allocation_status": "Active"
        }, format="json")
        self.assertEqual(res_approve.status_code, 200)

        xps_asset.refresh_from_db()
        self.assertEqual(xps_asset.asset_status, "Allocated")
        self.assertEqual(xps_asset.current_allocated_to, self.alice)
        self.assertEqual(xps_asset.current_allocation_id, alloc_id)

        # Verify OUT stock ledger
        alloc_ledger_count = AssetStockLedger.objects.filter(asset=xps_asset, trigger_type="Employee_Allocation").count()
        self.assertEqual(alloc_ledger_count, 1)

        # ----------------------------------------------------
        # 5. Unrelated Update Transition Guard (No Duplicate Ledger Writes)
        # ----------------------------------------------------
        res_edit = self.client.post(f"/api/populate/update/asset_allocation/{alloc_id}/", {
            "return_notes": "Updated allocation notes"
        }, format="json")
        self.assertEqual(res_edit.status_code, 200)
        # Ledger count must remain exactly 1
        self.assertEqual(AssetStockLedger.objects.filter(asset=xps_asset, trigger_type="Employee_Allocation").count(), 1)

        # ----------------------------------------------------
        # 6. Return Asset with Condition Reassessment
        # ----------------------------------------------------
        res_return = self.client.post(f"/api/populate/update/asset_allocation/{alloc_id}/", {
            "allocation_status": "Returned",
            "returned_condition": "Damaged",
            "return_notes": "Screen has horizontal flickering lines"
        }, format="json")
        self.assertEqual(res_return.status_code, 200)

        xps_asset.refresh_from_db()
        self.assertEqual(xps_asset.asset_status, "Available")
        self.assertIsNone(xps_asset.current_allocated_to)
        self.assertEqual(xps_asset.condition, "Damaged")
        self.assertTrue(AssetStockLedger.objects.filter(asset=xps_asset, trigger_type="Employee_Return").exists())

        # ----------------------------------------------------
        # 7. Repair Checkout & Return Lifecycle
        # ----------------------------------------------------
        res_repair = self.client.post("/api/populate/create/asset_repair/", {
            "asset": xps_asset.id,
            "vendor_name": "Dell Authorized Service Center",
            "repair_description": "Replace display panel"
        }, format="json")
        self.assertEqual(res_repair.status_code, 201)
        repair_item = res_repair.data["data"]
        repair_id = repair_item[0]["id"] if isinstance(repair_item, list) else repair_item["id"]

        xps_asset.refresh_from_db()
        self.assertEqual(xps_asset.asset_status, "Under Repair")
        self.assertTrue(AssetStockLedger.objects.filter(asset=xps_asset, trigger_type="Send_To_Repair").exists())

        # Close repair as Repaired with condition Good
        res_repaired = self.client.post(f"/api/populate/update/asset_repair/{repair_id}/", {
            "repair_status": "Repaired",
            "repair_condition": "Good",
            "repair_cost": 180.00
        }, format="json")
        self.assertEqual(res_repaired.status_code, 200)

        xps_asset.refresh_from_db()
        self.assertEqual(xps_asset.asset_status, "Available")
        self.assertEqual(xps_asset.condition, "Good")
        self.assertTrue(AssetStockLedger.objects.filter(asset=xps_asset, trigger_type="Repair_Return").exists())

        # ----------------------------------------------------
        # 8. Incident Reporting Anti-Spoofing & Loss Tracking
        # ----------------------------------------------------
        # Alice cannot report an incident attributed to Bob
        self.client.force_authenticate(user=self.alice)
        res_inc_spoof = self.client.post("/api/populate/create/asset_incident/", {
            "asset": xps_asset.id,
            "employee": self.bob.id,
            "incident_type": "Theft",
            "description": "Stolen from car"
        }, format="json")
        self.assertIn(res_inc_spoof.status_code, (400, 403))

        # Legitimate theft report by Alice
        res_inc = self.client.post("/api/populate/create/asset_incident/", {
            "asset": xps_asset.id,
            "incident_type": "Theft",
            "description": "Laptop bag stolen during transit"
        }, format="json")
        self.assertEqual(res_inc.status_code, 201)

        xps_asset.refresh_from_db()
        self.assertEqual(xps_asset.asset_status, "Lost")
        
        # Verify accurate ledger recording (new_state="Lost", trigger="Incident_Loss")
        lost_ledger = AssetStockLedger.objects.filter(asset=xps_asset, trigger_type="Incident_Loss").first()
        self.assertIsNotNone(lost_ledger)
        self.assertEqual(lost_ledger.new_state, "Lost")
