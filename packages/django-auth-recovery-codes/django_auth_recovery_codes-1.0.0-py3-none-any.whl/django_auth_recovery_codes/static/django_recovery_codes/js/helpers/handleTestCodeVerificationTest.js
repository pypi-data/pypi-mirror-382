import { handleButtonAlertClickHelper } from "./handleButtonAlertClicker.js";
import { handleFormSubmissionHelper } from "./formUtils.js";


/**
 * Handles the click event for verifying the test code setup.
 *
 * - Submits the test setup form.
 * - Prompts the user with an alert before verifying with the backend.
 * - Sends the verification request and processes the results.
 * - Updates UI elements, including spinners, messages, and form visibility.
 *
 * @param {Event} e - The click event from the verification button.
 * @param {HTMLFormElement} testSetupFormElement - The form element containing the verification code.
 */
export async function handleTestCodeVerificationSetupClick(e, testSetupFormElement) {

    const formData = await handleTestSetupFormSubmission(e, testSetupFormElement)

    if (!formData) return;

    const code = formData.verifyCode;

    const alertAttributes = {
        title: "Verify setup",
        text: `⚠️ Important: This application will now verify if your setup was correctly configured with the backend. 
                    This is a one time verification and will not be verified again on the next batch
                        Are you sure you want to continue?`,
        icon: "info",
        cancelMessage: "No worries! No action was taken",
        messageToDisplayOnSuccess: `
                    Great! Your codes are being verified, we let you know once it is ready.
                    You can continue using the app while we validate them.
                    We’ll notify you once they’re ready.
                    Please, don't close the page.
                `,
        confirmButtonText: "Yes, validate setup",
        denyButtonText: "No, don't validate setup"
    };

    const handleTestSetupFetchAPI = async () => {
        const data = await fetchData({
            url: "/auth/recovery-codes/verify-setup/",
            csrfToken: getCsrfToken(),
            method: "POST",
            body: { code: code },
            throwOnError: false,
        });

        return data;

    };

    const data = await handleButtonAlertClickHelper(e,
        VERIFY_SETUP_BUTTON,
        testVerifySpinnerElement,
        alertAttributes,
        handleTestSetupFetchAPI,
    );


    if (data) {

        try {
            const isComplete = await displayResults(data);

            if (!data.FAILURE) {
                toggleElement(dynamicTestFormSetupElement);

                try {
                    toggleElement(testSetupFormElement);
                } catch (error) {
                    doNothing();
                }
            }

            testFormSectionElement.reset();

            if (isComplete) {
                verificationTestComplete();
            }

        } catch (error) {
            doNothing();
        } 

}
}

/**
 * Handles the submission event for the "delete" form.
 *
 * The function allows the user to submit a request to delete a single recovery
 * codes via a fetch API request when the form is submitted.
 * 
 *
 *
 * @param {Event} e - The submit event triggered by the form.
 * @returns {void}
 */
function handleTestSetupFormSubmission(e, testSetupFormElement) {
    return handleFormSubmissionHelper(e, testSetupFormElement, ["verify_code"]);

}


