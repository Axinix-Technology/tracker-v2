import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '../../');
const BACKEND_DIR = path.resolve(ROOT_DIR, 'backend');
const FRONTEND_DIR = path.resolve(ROOT_DIR, 'Frontend/src');

/**
 * Audit: Pure API Contract & Postman Request Alignment
 * Verifies that all models, aliases, and auth routes align with
 * what Postman / Frontend receives over the wire.
 */
function checkApiContract() {
  console.log('======================================================');
  console.log('=== Pure API Contract & Postman Route Alignment   ===');
  console.log('======================================================');

  let errors = 0;
  let passed = 0;

  // 1. Verify Django URL Routing Configuration
  const urlsPyPath = path.join(BACKEND_DIR, 'config/urls.py');
  if (!fs.existsSync(urlsPyPath)) {
    console.error('🔴 Blocker: config/urls.py not found.');
    errors++;
  } else {
    const urlsContent = fs.readFileSync(urlsPyPath, 'utf8');
    if (urlsContent.includes('api/populate/') && urlsContent.includes('api/auth/')) {
      console.log('✅ PASS: Core API routes registered (/api/populate/, /api/auth/).');
      passed++;
    } else {
      console.error('🔴 Blocker: Missing /api/populate/ or /api/auth/ routing in config/urls.py.');
      errors++;
    }
  }

  // 2. Verify Auth Handshake Endpoints
  const authUrlsPath = path.join(BACKEND_DIR, 'users/urls.py');
  if (fs.existsSync(authUrlsPath)) {
    const authContent = fs.readFileSync(authUrlsPath, 'utf8');
    const requiredEndpoints = ['login', 'logout', 'change-password', 'me/context'];
    requiredEndpoints.forEach(ep => {
      if (authContent.includes(ep)) {
        console.log(`✅ PASS: Auth endpoint exposed for Postman: /api/auth/${ep}`);
        passed++;
      } else {
        console.error(`🔴 Blocker: Auth endpoint /api/auth/${ep} missing.`);
        errors++;
      }
    });
  }

  // 3. Verify Critical Frontend Aliases in Django Models
  const aliasChecks = [
    {
      file: 'hr/models.py',
      model: 'EmployeeLifecycleHistory',
      alias: 'employee_life_cycle_histories'
    },
    {
      file: 'payroll/models.py',
      model: 'Payroll',
      alias: 'payslips'
    },
    {
      file: 'system/models.py',
      model: 'StatusConfig',
      alias: 'status_configss'
    },
    {
      file: 'billing/models.py',
      model: 'OrderAcknowledgement',
      alias: 'oa'
    },
    {
      file: 'billing/models.py',
      model: 'ClientLedger',
      alias: 'clients_ledgers'
    },
    {
      file: 'notifications/models.py',
      model: 'NotificationRule',
      alias: 'notificationrules'
    }
  ];

  aliasChecks.forEach(({ file, model, alias }) => {
    const filePath = path.join(BACKEND_DIR, file);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      if (content.includes(alias)) {
        console.log(`✅ PASS: Alias '${alias}' registered for '${model}'.`);
        passed++;
      } else {
        console.error(`🔴 Blocker: Alias '${alias}' missing in ${file} for model ${model}.`);
        errors++;
      }
    } else {
      console.error(`🔴 Blocker: File ${file} not found.`);
      errors++;
    }
  });

  // 4. Verify Immutable Ledger Registrations
  const ledgerChecks = [
    { file: 'billing/models.py', model: 'ClientLedger' },
    { file: 'billing/models.py', model: 'QuotationRevision' },
    { file: 'assets/models.py', model: 'AssetStockLedger' }
  ];

  ledgerChecks.forEach(({ file, model }) => {
    const filePath = path.join(BACKEND_DIR, file);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      if (content.includes('table_type="ledger"') || content.includes("allow_direct_update=False")) {
        console.log(`✅ PASS: '${model}' in ${file} enforces immutable ledger policy.`);
        passed++;
      } else {
        console.error(`🔴 Blocker: Ledger immutability not configured for ${model} in ${file}.`);
        errors++;
      }
    }
  });

  console.log('------------------------------------------------------');
  if (errors === 0) {
    console.log(`✅ ALL CHECKS PASSED: ${passed} API contract checks verified.`);
    process.exit(0);
  } else {
    console.error(`❌ FAILED: ${errors} contract violations found.`);
    process.exit(1);
  }
}

checkApiContract();

