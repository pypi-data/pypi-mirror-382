/**
 * @typedef {Object} Contact
 * @property {string} ContactName
 * @property {string} EmailAddress
 * @property {string} MobilePhone
 */
/**
 * @typedef {Object} Address
 * @property {string} BusinessName
 * @property {string[]} AddressLines
 * @property {string} Town
 * @property {string} Postcode
 * @property {string} [Country = 'GB']
 */
/**
 * @typedef {Object} AddrChoice
 * @property {Address} Address
 * @property {Number} Score
 */

/**
 * @typedef {Object} FullContact
 * @property {Contact} Contact
 * @property {Address} Address
 */

/**
 * @typedef {Object} Shipment
 * @property {FullContact} Recipient
 * @property {FullContact} [Sender]
 * @property {number} Boxes
 * @property {string} ShippingDate
 * @property {string} Reference
 * @property {string} SpecialInstructions1
 * @property {string} SpecialInstructions2
 * @property {string} SpecialInstructions3
 * @property {Object} Context
 * @property {string} Direction
 */

/**
 * @typedef {Object} ShipmentRequest
 * @property {Shipment} Shipment
 * @property {string} Provider
 */


// FILL FORM FROM CONTEXT
/**
 * Initialize the ship form with shipment data.
 * @param {Shipment} shipment - The shipment data.
 */
async function initShipForm(shipment) {
    console.log('Initializing ship form with shipment:', shipment);
    populateShipment(shipment);

    const contextjson = JSON.stringify(shipment.Context);
    await setContextJson(contextjson);
    await loadAddrChoices();
    setProvider();
    // checkToggleOwnLabel();
    // toggleCollectionTimes();
}

async function setContextJson(contextJson) {
    const contextJsonInput = document.querySelector('input[name="context_json"]');
    contextJsonInput.value = contextJson;
    console.log('contextJsonInput.value', contextJsonInput.value);

}


/**
 * Populates form fields with shipment data.
 // * @param {Shipment} shipment - The shipment data in snake_case.
 */
function populateShipment(shipment) {
    console.log('Populating form from shipment');

    document.getElementById('ship_date').value = shipment.ShippingDate;
    document.getElementById('boxes').value = shipment.Boxes || 1;
    document.getElementById('reference').value = shipment.Reference || "";
    document.getElementById('business_name').value = shipment.Recipient.Address.BusinessName || "";
    document.getElementById('contact_name').value = shipment.Recipient.Contact.ContactName || "";
    document.getElementById('email').value = shipment.Recipient.Contact.EmailAddress || "";
    document.getElementById('mobile_phone').value = shipment.Recipient.Contact.MobilePhone || "";
    document.getElementById('address_line1').value = shipment.Recipient.Address.AddressLines[0] || "";
    document.getElementById('address_line2').value = shipment.Recipient.Address.AddressLines[1] || "";
    document.getElementById('address_line3').value = shipment.Recipient.Address.AddressLines[2] || "";
    document.getElementById('town').value = shipment.Recipient.Address.Town || "";
    document.getElementById('postcode').value = shipment.Recipient.Address.Postcode || "";
}


function toggleDiv(idToToggle, toggleOn) {
    let elementToToggle = document.getElementById(idToToggle);
    if (toggleOn) {
        console.log(`Showing ${idToToggle}`);
        elementToToggle.style.opacity = '100';
    } else {
        console.log(`Hiding ${idToToggle}`);
        elementToToggle.style.opacity = '0'
    }

}

function checkToggleDiv(idToCheck, idToToggle, conditionToShow) {
    let valueToCheck = document.getElementById(idToCheck).value;
    if (valueToCheck === conditionToShow) {
        toggleDiv(idToToggle, true);
    } else {
        toggleDiv(idToToggle, false);
    }
}

//
//
// function directionChange() {
//     if (document.getElementById('provider_name').value === 'APC') {
//         setProviderAPC();
//     } else if (document.getElementById('provider_name').value === 'PARCELFORCE') {
//         setProviderParcelforce();
//     }
// }


function setProvider() {
    console.log('Setting provider based on selection');
    let provider = document.getElementById('provider_name').value;
    if (provider === 'PARCELFORCE') {
        setProviderParcelforce();
    } else if (provider === 'APC') {
        setProviderAPC();
    } else {
        console.warn('Unknown provider selected:', provider);
    }

}

function setProviderParcelforce() {
    console.log('Setting provider to PARCELFORCE');
    toggleDiv('collect_times', false);
    checkToggleDiv("direction", "own_label", "in");
}

function setProviderAPC() {
    console.log('Setting provider to APC');
    toggleDiv('own_label', false);
    checkToggleDiv('direction', 'collect_times', 'in');
}

// GATHER FORM DATA
function contactFromForm() {
    return {
        ContactName: document.getElementById('contact_name').value,
        EmailAddress: document.getElementById('email').value,
        MobilePhone: document.getElementById('mobile_phone').value,
    };
}

function addressFromForm() {
    return {
        AddressLines: [document.getElementById('address_line1').value, document.getElementById('address_line2').value, document.getElementById('address_line3').value].filter(line => line),
        Town: document.getElementById('town').value,
        Postcode: document.getElementById('postcode').value,
        BusinessName: document.getElementById('business_name').value || "",
    };
}

function shipmentFromForm() {
    return {
        Recipient: {
            Contact: contactFromForm(), Address: addressFromForm()
        },
        Boxes: parseInt(document.getElementById('boxes').value, 10) || 1,
        ShippingDate: document.getElementById('ship_date').value,
        Direction: document.getElementById('direction').value || "out",
        Reference: document.getElementById('reference').value || "",
        Service: document.getElementById('service').value || "",

    };
}

function shipmentRequestFromForm() {
    return {
        Shipment: shipmentFromForm(), ProviderName: document.getElementById('provider').value
    }
}


// ADDRESS CHOICES / CANDIDATE LOOKUP
async function loadAddrChoices() {
    // get address from form fields
    const address = addressFromForm();
    console.log('Loading AddressChoices for address:', address);
    // fetch AddressChices from server
    const addrChoicesJson = await fetchAddrChoices(address.Postcode, address);
    // populate address-select options and 'click to insert' div
    await handleAddrChoices(addrChoicesJson);
}

/**
 * Get AddressChoices from server.
 * @param {String} Postcode
 * @param {Address} Address - The address to search.
 * @returns {Promise<AddrChoice[]>}
 */
async function fetchAddrChoices(Postcode, Address) {
    const addrChoiceUrl = 'api/addr_choices';
    console.log(`Posting to ${addrChoiceUrl} pc=${Postcode}, add=${Address}`);
    try {
        const response = await fetch(addrChoiceUrl, {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({
                postcode: Postcode, address: Address
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Error fetching candidates:', error);
    }
}

/**
 * Handles AddressChoices from server.
 * @param {AddrChoice[]} addrChoices
 */
function handleAddrChoices(addrChoices) {

    console.log('HANDLING ADDR CHOICES', addrChoices);
    let highestScoreOption = null;
    let highestScore = -Infinity;
    const addressSelect = document.getElementById('address-select');
    addressSelect.innerHTML = '';

    addrChoices.forEach(choice => {
        const option = addrChoiceOption(choice);
        if (choice.Score > highestScore) {
            highestScore = choice.Score;
            highestScoreOption = option;
        }
        addressSelect.appendChild(option);
    });

    if (highestScoreOption) {
        console.log('Match Score', highestScore, '%', highestScoreOption.value);
        highestScoreOption.selected = true;
        setScoreSpan(highestScoreOption);
    }
}

/**
 * Create an option element for an AddressChoice.
 * @param {AddrChoice} addressChoice
 * @returns {HTMLOptionElement}
 */
function addrChoiceOption(addressChoice) {
    const option = document.createElement('option');
    option.value = JSON.stringify(addressChoice.Address);
    option.textContent = addressLinesOutput(addressChoice.Address, ', ');
    option.dataset.score = addressChoice.Score.toString();
    return option;
}

// UPDATE FORM
/**
 * Update address fields with given address data.
 * @param {Address} Address
 */
function updateAddressFields(Address) {
    console.log('Updating manual fields');
    document.getElementById('address_line1').value = Address.AddressLines[0] || '';
    document.getElementById('address_line2').value = Address.AddressLines?.[1] || '';
    document.getElementById('address_line3').value = Address.AddressLines?.[2] || '';
    document.getElementById('town').value = Address.Town || '';
    document.getElementById('postcode').value = Address.Postcode || '';
}

function updateAddressFromSelect() {
    const selectedOption = document.getElementById('address-select').value;
    updateAddressFieldsFromJson(selectedOption);
}

function updateAddressFieldsFromJson(address_json) {
    const address = JSON.parse(address_json);
    updateAddressFields(address);
}

function scoreCssSelector(score) {
    if (score > 80) return 'high-score';
    if (score >= 60) return 'medium-score';
    return 'low-score';
}


function setScoreSpan(option) {
    const scoreSpan = document.getElementById('score-span');
    const address = JSON.parse(option.value);
    const score = parseInt(option.dataset.score, 10) || 0;
    const addressHtml = addressLinesOutput(address, '<br>');

    scoreSpan.className = scoreCssSelector(score);
    scoreSpan.innerHTML = `Best Guess (click to insert)<br>${addressHtml}`;
    scoreSpan.onclick = updateAddressFromSelect;
}

function addressLinesOutput(Address, Seperator) {
    return getAddressLines(Address).join(Seperator);
}

/**
 * Get non-empty address lines from Address object.
 * @param {Address} Address
 * @returns {string[]}
 */
function getAddressLines(Address) {
    return [...Address.AddressLines]
        .filter(line => line);
}


