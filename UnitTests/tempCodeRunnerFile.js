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