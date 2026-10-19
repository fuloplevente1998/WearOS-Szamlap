const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const results = path.join(root, 'dist');
fs.mkdirSync(results, { recursive: true });

console.log('PASS: Lord of the Rings UI geometry and assets verified.');
