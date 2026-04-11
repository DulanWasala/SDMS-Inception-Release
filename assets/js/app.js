const STORAGE_KEY = "sdmsAssignedEquipmentClean";

function clearAssignment() {
  localStorage.removeItem(STORAGE_KEY);
}

function saveAssignment(payload) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
}

function getAssignment() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (err) {
    return null;
  }
}

function renderEmployeeInfo() {
  const assignedArea = document.getElementById("assignedEquipmentArea");
  const successBox = document.getElementById("successMessage");
  if (!assignedArea) return;

  const item = getAssignment();

  if (!item) {
    assignedArea.innerHTML = '<div class="equipment-card empty">No equipment currently assigned</div>';
    if (successBox) successBox.style.display = "none";
    return;
  }

  assignedArea.innerHTML = `
    <div class="equipment-card">
      <div><strong>Item:</strong> ${item.itemName}</div>
      <div><strong>Item ID:</strong> ${item.itemId}</div>
      <div><strong>Item Type:</strong> ${item.itemType}</div>
      <div><strong>Time Out:</strong> ${item.timeOut}</div>
      <div><strong>Condition:</strong> ${item.condition}</div>
    </div>
  `;

  if (successBox && window.location.search.includes("updated=1")) {
    successBox.style.display = "block";
    successBox.textContent = `${item.itemName} with ID ${item.itemId} has been assigned to John Smith at ${item.timeOut}.`;
  } else if (successBox) {
    successBox.style.display = "none";
  }
}

function showSignoutModal(itemId, itemName, itemType) {
  const modal = document.getElementById("signoutModal");
  if (!modal) return;
  document.getElementById("modalItemId").textContent = itemId;
  document.getElementById("modalItemName").textContent = itemName;
  document.getElementById("modalItemType").textContent = itemType;
  modal.classList.add("show");
}

function hideSignoutModal() {
  const modal = document.getElementById("signoutModal");
  if (modal) modal.classList.remove("show");
}

function confirmEquipmentSignout() {
  const condition = document.getElementById("conditionSelect").value;
  const itemId = document.getElementById("modalItemId").textContent;
  const itemName = document.getElementById("modalItemName").textContent;
  const itemType = document.getElementById("modalItemType").textContent;

  saveAssignment({
    itemId,
    itemName,
    itemType,
    condition,
    timeOut: "10:30 AM"
  });

  window.location.href = "employee-info.html?updated=1";
}

/* =========================
   LOST & FOUND MOCK BACKEND
   ========================= */

const LOST_FOUND_ITEMS_KEY = "sdmsLostFoundItems";
const LOST_FOUND_CLAIMS_KEY = "sdmsLostFoundClaims";
const LOST_FOUND_AUDIT_KEY = "sdmsLostFoundAudit";

function getNowString() {
  return new Date().toLocaleString();
}

function safeReadJson(key, fallback) {
  const raw = localStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw);
  } catch (err) {
    return fallback;
  }
}

function safeWriteJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function seedLostFoundData() {
  const existingItems = safeReadJson(LOST_FOUND_ITEMS_KEY, null);
  if (!existingItems) {
    safeWriteJson(LOST_FOUND_ITEMS_KEY, [
      {
        itemId: "LF001",
        description: "Black Wallet",
        status: "Found",
        dateReported: "2026-03-08",
        locationFound: "Break Room",
        storageLocation: "Lost & Found Shelf A",
        notes: "Wallet found near vending machines."
      },
      {
        itemId: "LF002",
        description: "Blue Water Bottle",
        status: "Lost",
        dateReported: "2026-03-07",
        locationFound: "N/A",
        storageLocation: "N/A",
        notes: "Reported missing by warehouse associate."
      },
      {
        itemId: "LF003",
        description: "Employee Badge",
        status: "Claimed",
        dateReported: "2026-03-06",
        locationFound: "Security Desk",
        storageLocation: "Released",
        notes: "Previously claimed by employee."
      }
    ]);
  }

  const existingClaims = safeReadJson(LOST_FOUND_CLAIMS_KEY, null);
  if (!existingClaims) {
    safeWriteJson(LOST_FOUND_CLAIMS_KEY, []);
  }

  const existingAudit = safeReadJson(LOST_FOUND_AUDIT_KEY, null);
  if (!existingAudit) {
    safeWriteJson(LOST_FOUND_AUDIT_KEY, []);
  }
}

/* ============
   REPOSITORIES
   ============ */

class FoundItemRepository {
  findAll() {
    return safeReadJson(LOST_FOUND_ITEMS_KEY, []);
  }

  findFoundItemById(itemId) {
    return this.findAll().find(item => item.itemId === itemId) || null;
  }

  updateItemStatus(itemId, status) {
    const items = this.findAll();
    const index = items.findIndex(item => item.itemId === itemId);

    if (index === -1) {
      return null;
    }

    items[index].status = status;
    safeWriteJson(LOST_FOUND_ITEMS_KEY, items);
    return items[index];
  }
}

class ClaimRepository {
  findAll() {
    return safeReadJson(LOST_FOUND_CLAIMS_KEY, []);
  }

  saveClaim(claim) {
    const claims = this.findAll();
    claims.push(claim);
    safeWriteJson(LOST_FOUND_CLAIMS_KEY, claims);
    return claim;
  }
}

class AuditLogRepository {
  findAll() {
    return safeReadJson(LOST_FOUND_AUDIT_KEY, []);
  }

  recordEvent(eventDescription, itemId) {
    const events = this.findAll();
    events.push({
      eventId: `AUD-${Date.now()}`,
      itemId,
      description: eventDescription,
      timestamp: getNowString()
    });
    safeWriteJson(LOST_FOUND_AUDIT_KEY, events);
    return true;
  }
}

/* ========
   SERVICES
   ======== */

class ClaimService {
  constructor(foundItemRepository, claimRepository, auditLogRepository) {
    this.foundItemRepository = foundItemRepository;
    this.claimRepository = claimRepository;
    this.auditLogRepository = auditLogRepository;
  }

  validateClaimable(foundItem) {
    if (!foundItem) {
      return { ok: false, message: "Item could not be found." };
    }

    if (foundItem.status !== "Found") {
      return {
        ok: false,
        message: `This item cannot be claimed because its current status is "${foundItem.status}".`
      };
    }

    return { ok: true };
  }

  submitClaim(itemId, claimantInfo) {
    const foundItem = this.foundItemRepository.findFoundItemById(itemId);
    const validation = this.validateClaimable(foundItem);

    if (!validation.ok) {
      return validation;
    }

    const claim = {
      claimId: `CLM-${Date.now()}`,
      itemId,
      claimantName: claimantInfo.name,
      claimantId: claimantInfo.personId,
      claimDate: getNowString(),
      verificationStatus: "Pending",
      claimStatus: "Submitted"
    };

    this.claimRepository.saveClaim(claim);
    this.foundItemRepository.updateItemStatus(itemId, "Pending Verification");
    this.auditLogRepository.recordEvent("Claim submitted for found item", itemId);

    return {
      ok: true,
      message: `Claim request submitted for item ${itemId}. Verification is now pending.`,
      claim
    };
  }
}

/* ==========
   CONTROLLER
   ========== */

class LostFoundController {
  constructor() {
    this.foundItemRepository = new FoundItemRepository();
    this.claimRepository = new ClaimRepository();
    this.auditLogRepository = new AuditLogRepository();
    this.claimService = new ClaimService(
      this.foundItemRepository,
      this.claimRepository,
      this.auditLogRepository
    );
  }

  submitClaim(itemId, claimantInfo) {
    return this.claimService.submitClaim(itemId, claimantInfo);
  }

  getItemDetails(itemId) {
    return this.foundItemRepository.findFoundItemById(itemId);
  }

  getAllItems() {
    return this.foundItemRepository.findAll();
  }
}

/* =====================
   LOST & FOUND UI LOGIC
   ===================== */

const lostFoundController = new LostFoundController();

function getSelectedItemId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("itemId") || "LF001";
}

function renderLostFoundSearch() {
  const resultsArea = document.getElementById("lostFoundResults");
  if (!resultsArea) return;

  const items = lostFoundController.getAllItems();

  resultsArea.innerHTML = items.map(item => `
    <a
      class="equipment-row"
      href="item-details.html?itemId=${encodeURIComponent(item.itemId)}"
      style="display:block; color:inherit; text-decoration:none;"
    >
      ${item.itemId} | ${item.description} | ${item.status} | ${item.dateReported}
    </a>
  `).join("");
}

function renderLostFoundItemDetails() {
  const itemInfoArea = document.getElementById("lostFoundItemInfo");
  const claimInfoArea = document.getElementById("lostFoundClaimInfo");
  const claimButton = document.getElementById("claimItemButton");
  if (!itemInfoArea) return;

  const itemId = getSelectedItemId();
  const item = lostFoundController.getItemDetails(itemId);

  if (!item) {
    itemInfoArea.innerHTML = `<div class="info-lines"><div><strong>Error:</strong> Item not found.</div></div>`;
    if (claimInfoArea) {
      claimInfoArea.innerHTML = `<div class="info-lines"><div>No claim information available.</div></div>`;
    }
    if (claimButton) {
      claimButton.style.display = "none";
    }
    return;
  }

  itemInfoArea.innerHTML = `
    <div class="info-lines">
      <div><strong>Item ID:</strong> ${item.itemId}</div>
      <div><strong>Description:</strong> ${item.description}</div>
      <div><strong>Status:</strong> ${item.status}</div>
      <div><strong>Date Reported:</strong> ${item.dateReported}</div>
      <div><strong>Location Found:</strong> ${item.locationFound}</div>
      <div><strong>Storage Location:</strong> ${item.storageLocation}</div>
    </div>
  `;

  const claims = safeReadJson(LOST_FOUND_CLAIMS_KEY, []);
  const latestClaim = claims.filter(claim => claim.itemId === item.itemId).slice(-1)[0];

  if (latestClaim) {
    claimInfoArea.innerHTML = `
      <div class="info-lines">
        <div><strong>Claimant Name:</strong> ${latestClaim.claimantName}</div>
        <div><strong>Employee ID:</strong> ${latestClaim.claimantId}</div>
        <div><strong>Verification Status:</strong> ${latestClaim.verificationStatus}</div>
        <div><strong>Claim Status:</strong> ${latestClaim.claimStatus}</div>
      </div>
    `;
  } else {
    claimInfoArea.innerHTML = `
      <div class="info-lines">
        <div><strong>Claimant Name:</strong> John Smith</div>
        <div><strong>Employee ID:</strong> E1023</div>
        <div><strong>Verification Status:</strong> None</div>
      </div>
    `;
  }

  if (claimButton) {
    if (item.status !== "Found") {
      claimButton.classList.add("secondary");
      claimButton.textContent = "Item Not Claimable";
      claimButton.onclick = function () {
        alert(`This item cannot be claimed because its current status is "${item.status}".`);
        return false;
      };
    }
  }
}

function claimCurrentLostFoundItem() {
  const successBox = document.getElementById("claimSuccessMessage");
  const itemId = getSelectedItemId();

  const claimantInfo = {
    personId: "E1023",
    name: "John Smith"
  };

  const result = lostFoundController.submitClaim(itemId, claimantInfo);

  if (!successBox) return;

  successBox.style.display = "block";
  successBox.textContent = result.message;

  if (result.ok) {
    renderLostFoundItemDetails();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderEmployeeInfo();
  seedLostFoundData();
  renderLostFoundSearch();
  renderLostFoundItemDetails();

  document.querySelectorAll("[data-reset-assignment='true']").forEach(el => {
    el.addEventListener("click", clearAssignment);
  });
});