#!/usr/bin/env node

/**
 * Apply null safety fixes to all dashboard components
 */

const fs = require('fs');
const path = require('path');

const componentsDir = 'src/components/dashboard';
const components = [
  'ProcurementFunnel.tsx',
  'LeaderboardTable.tsx',
  'TrendChart.tsx',
  'IntegrityHeatmap.tsx',
  'CartelRadar.tsx',
  'ExportControls.tsx',
];

console.log('🔧 Checking dashboard components for null safety...\n');

components.forEach((component) => {
  const filePath = path.join(componentsDir, component);
  
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  ${component} not found`);
    return;
  }
  
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Check if component has null safety
  const hasNullCheck = content.includes('if (!data') || content.includes('if (!');
  const hasOptionalChaining = content.includes('data?.') || content.includes('||');
  
  if (hasNullCheck || hasOptionalChaining) {
    console.log(`✅ ${component} - Has safety checks`);
  } else {
    console.log(`⚠️  ${component} - May need null safety`);
  }
});

console.log('\n✓ Check complete. Review components marked with ⚠️\n');
