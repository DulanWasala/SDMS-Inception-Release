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

document.addEventListener("DOMContentLoaded", () => {
  renderEmployeeInfo();

  document.querySelectorAll("[data-reset-assignment='true']").forEach(el => {
    el.addEventListener("click", clearAssignment);
  });
});
