import { initAll } from 'govuk-frontend';
import { initAll as initAllMOJ } from '@ministryofjustice/frontend';
import { FilterToggleButton } from '@ministryofjustice/frontend/moj/components/filter-toggle-button/filter-toggle-button.mjs';

initAll();
initAllMOJ();

// Export FilterToggleButton to global scope so templates can use it
window.FilterToggleButton = FilterToggleButton;

// Dispatch event to signal FilterToggleButton is ready
window.dispatchEvent(new Event('FilterToggleButtonReady'));
