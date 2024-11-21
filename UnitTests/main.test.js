import { SearchManager } from '../stroke_prediction/app/static/js/main';
import { showToast, fetchWithCSRF } from '../stroke_prediction/app/static/js/main';

jest.mock('../stroke_prediction/app/static/js/main', () => ({
    showToast: jest.fn(),
    fetchWithCSRF: jest.fn(),
}));

describe('SearchManager', () => {
    let searchManager;
    let mockForm;
    let mockInput;
    let mockPatientDetails;

    beforeEach(() => {
        document.body.innerHTML = `
      <form id="search-form">
        <input name="patient_id" value="SW123456789" />
      </form>
      <div id="patient-details"></div>
    `;

        mockForm = document.getElementById('search-form');
        mockInput = mockForm.querySelector('input[name="patient_id"]');
        mockPatientDetails = document.getElementById('patient-details');

        searchManager = new SearchManager();
        searchManager.PREFIX = 'SW';
        searchManager.MAX_DIGITS = 9;
        searchManager.patientDetails = mockPatientDetails;
    });
});

test('Should correctly extract the numeric value from the input by removing the prefix', async () => {
    const mockEvent = {
        preventDefault: jest.fn(),
        target: {
            querySelector: jest.fn().mockReturnValue({
                value: 'SW123456789'
            })
        }
    };

    await searchManager.handleSearch(mockEvent);

    expect(mockEvent.target.querySelector).toHaveBeenCalledWith('input[name="patient_id"]');
    expect(fetchWithCSRF).toHaveBeenCalledWith(
        expect.stringContaining('patient_id=123456789'),
        expect.any(Object)
    );
});