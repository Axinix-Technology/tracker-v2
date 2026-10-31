import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '../../');
const BACKEND_DIR = path.resolve(ROOT_DIR, 'backend');

function auditAllModelsStatusField() {
  console.log('=== Verifying Mandatory Status Field Across All Django Models ===');

  const apps = [
    'users', 'attendance', 'tasks', 'tickets', 'assets', 'notifications',
    'dashboard', 'feed', 'hr', 'payroll', 'billing', 'crm', 'recruitment',
    'system', 'control_plane'
  ];

  let errors = 0;
  let modelsChecked = 0;

  apps.forEach(app => {
    const modelsFile = path.join(BACKEND_DIR, app, 'models.py');
    if (!fs.existsSync(modelsFile)) return;

    const content = fs.readFileSync(modelsFile, 'utf8');
    const lines = content.split('\n');

    let currentDecorator = null;
    let currentModelName = null;
    let currentModelClass = null;
    let modelLines = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.includes('@register_model')) {
        currentDecorator = line;
        let j = i;
        while (!lines[j].includes(')') && j < lines.length - 1) {
          j++;
          currentDecorator += '\n' + lines[j];
        }
      }

      if (line.startsWith('class ') && line.includes('(models.Model):')) {
        const match = line.match(/class\s+([A-Za-z0-9_]+)\s*\(/);
        if (match) {
          currentModelClass = match[1];
          modelsChecked++;
          
          // Determine expected status field from decorator
          let expectedStatusField = 'status';
          let tableType = 'master';

          if (currentDecorator) {
            const statusMatch = currentDecorator.match(/status_field\s*=\s*["']([^"']+)["']/);
            if (statusMatch) {
              expectedStatusField = statusMatch[1];
            }
            const typeMatch = currentDecorator.match(/table_type\s*=\s*["']([^"']+)["']/);
            if (typeMatch) {
              tableType = typeMatch[1];
            }
          }

          // Check if ledger
          if (tableType === 'ledger') {
            // Ledgers don't require 0/1 active-inactive check according to E001
            currentDecorator = null;
            continue;
          }

          // Collect lines for this model class until next class or EOF
          let k = i + 1;
          let classBody = '';
          while (k < lines.length && !lines[k].startsWith('class ') && !lines[k].startsWith('@register_model')) {
            classBody += lines[k] + '\n';
            k++;
          }

          // Check if classBody defines expectedStatusField
          const fieldRegex = new RegExp(`^\\s+${expectedStatusField}\\s*=`, 'm');
          if (!fieldRegex.test(classBody)) {
            console.error(`❌ Blocker: Model '${currentModelClass}' in app '${app}' requires field '${expectedStatusField}', but it is missing!`);
            errors++;
          } else {
            // console.log(`✓ ${app}.${currentModelClass}: '${expectedStatusField}' present.`);
          }

          currentDecorator = null;
        }
      }
    }
  });

  console.log(`Audited ${modelsChecked} models.`);
  if (errors === 0) {
    console.log('✅ PASS: All models define their required status field.');
  } else {
    console.error(`❌ FAILED: ${errors} models have missing status fields.`);
    process.exit(1);
  }
}

auditAllModelsStatusField();

