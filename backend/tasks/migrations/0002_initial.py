# Generated for linking tasks and tickets
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='linkedTicketId',
            field=models.ForeignKey(blank=True, db_column='linked_ticket_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='linked_tasks', to='tickets.ticket'),
        ),
    ]
