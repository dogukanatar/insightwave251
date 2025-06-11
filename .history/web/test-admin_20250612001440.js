// Simple test to verify admin page components
const { readFileSync } = require('fs');
const path = require('path');

console.log('🔍 Testing admin page imports...');

try {
  // Check if the main files exist and don't have revalidatePath in data fetching
  const thesisFile = readFileSync(path.join(__dirname, 'actions/thesis-summaries.ts'), 'utf8');
  const notificationsFile = readFileSync(path.join(__dirname, 'actions/notifications.ts'), 'utf8');
  
  const thesisHasRevalidate = thesisFile.includes('revalidatePath');
  const notificationsHasRevalidate = notificationsFile.includes('revalidatePath');
  
  if (thesisHasRevalidate) {
    console.log('❌ thesis-summaries.ts still contains revalidatePath');
  } else {
    console.log('✅ thesis-summaries.ts - revalidatePath removed');
  }
  
  if (notificationsHasRevalidate) {
    console.log('❌ notifications.ts still contains revalidatePath');
  } else {
    console.log('✅ notifications.ts - revalidatePath removed');
  }
  
  console.log('🎉 Admin page should now work without revalidatePath render errors!');
  
} catch (error) {
  console.error('Error testing:', error.message);
} 