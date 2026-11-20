/* ScholarTrack dashboard: browser-side interactions and Chart.js visualizations. */

const SUBJECTS = window.SUBJECTS || [];
const SUBJECT_COLUMNS = window.SUBJECT_COLUMNS || [];
const charts = {};
let editingStudentId = null;
let toastTimer = null;

const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[character]));
}

function currentFilters() {
  return {
    department: $("#departmentFilter").value,
    semester: $("#semesterFilter").value
  };
}

function queryString(values) {
  const params = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) params.set(key, value);
  });
  return params.toString();
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Something went wrong. Please try again.");
  return data;
}

function showToast(message, isError = false) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3000);
}

function setKpi(id, value) {
  const element = $(id);
  if (element) element.textContent = value;
}

function chartBaseOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#172849",
        padding: 10,
        titleFont: { family: "DM Sans", size: 11, weight: "600" },
        bodyFont: { family: "DM Sans", size: 10 }
      }
    }
  };
}

function replaceChart(key, canvasId, config) {
  if (charts[key]) charts[key].destroy();
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  charts[key] = new Chart(canvas, config);
}

function renderLegend(containerId, labels, values, colors) {
  const container = $(containerId);
  if (!container) return;
  container.innerHTML = labels.map((label, index) => `
    <span class="legend-item"><i class="legend-dot" style="background:${colors[index % colors.length]}"></i>
    ${escapeHtml(label)} <b>${Number(values[index] || 0)}</b></span>
  `).join("");
}

function renderCharts(data) {
  if (typeof Chart === "undefined") {
    console.warn("Chart.js did not load. Check your internet connection to display charts.");
    return;
  }
  const palette = ["#467fe5", "#7a65d4", "#19ad9d", "#e7a446", "#ed7894", "#54a7c8", "#a4b5ce"];
  const base = chartBaseOptions();

  replaceChart("subject", "subjectChart", {
    type: "bar",
    data: {
      labels: data.subject_labels,
      datasets: [{
        label: "Average marks",
        data: data.subject_averages,
        backgroundColor: ["#477fe7", "#7966d4", "#20a99c", "#e8a64d", "#6badd0", "#b18bd9"],
        borderRadius: 6,
        maxBarThickness: 38
      }]
    },
    options: {
      ...base,
      scales: {
        x: { grid: { display: false }, ticks: { color: "#8996aa", font: { size: 9 } } },
        y: { beginAtZero: true, max: 100, grid: { color: "#eef1f6", drawBorder: false }, ticks: { color: "#9aa5b6", font: { size: 9 }, stepSize: 20 } }
      }
    }
  });

  replaceChart("grade", "gradeChart", {
    type: "doughnut",
    data: { labels: data.grade_labels, datasets: [{ data: data.grade_values, backgroundColor: palette, borderWidth: 3, borderColor: "#fff", hoverOffset: 5 }] },
    options: { ...base, cutout: "69%", plugins: { ...base.plugins, tooltip: base.plugins.tooltip } }
  });
  renderLegend("#gradeLegend", data.grade_labels, data.grade_values, palette);

  const resultColors = ["#18aa91", "#e87878"];
  replaceChart("result", "resultChart", {
    type: "doughnut",
    data: { labels: data.result_labels, datasets: [{ data: data.result_values, backgroundColor: resultColors, borderWidth: 3, borderColor: "#fff", hoverOffset: 5 }] },
    options: { ...base, cutout: "69%" }
  });
  renderLegend("#resultLegend", data.result_labels, data.result_values, resultColors);

  replaceChart("department", "departmentChart", {
    type: "bar",
    data: { labels: data.department_labels, datasets: [{ label: "Average score", data: data.department_averages, backgroundColor: "#4b83e8", borderRadius: 5, maxBarThickness: 30 }] },
    options: {
      ...base,
      indexAxis: "y",
      scales: {
        x: { beginAtZero: true, max: 100, grid: { color: "#eef1f6", drawBorder: false }, ticks: { color: "#9aa5b6", font: { size: 9 } } },
        y: { grid: { display: false }, ticks: { color: "#71809a", font: { size: 9 } } }
      }
    }
  });

  replaceChart("semester", "semesterChart", {
    type: "line",
    data: { labels: data.semester_labels, datasets: [{ label: "Average score", data: data.semester_averages, borderColor: "#7b68d7", backgroundColor: "rgba(123,104,215,.12)", fill: true, tension: .35, borderWidth: 2.5, pointRadius: 4, pointBackgroundColor: "#7b68d7", pointBorderColor: "#fff", pointBorderWidth: 2 }] },
    options: {
      ...base,
      scales: {
        x: { grid: { display: false }, ticks: { color: "#8996aa", font: { size: 9 } } },
        y: { beginAtZero: true, max: 100, grid: { color: "#eef1f6", drawBorder: false }, ticks: { color: "#9aa5b6", font: { size: 9 } } }
      }
    }
  });
}

async function loadDashboard() {
  const data = await apiRequest(`/api/dashboard?${queryString(currentFilters())}`);
  setKpi("#totalStudents", data.total_students);
  setKpi("#averageScore", Number(data.average_score).toFixed(1));
  setKpi("#passRate", Number(data.pass_rate).toFixed(1));
  setKpi("#averageAttendance", Number(data.average_attendance).toFixed(1));
  setKpi("#topStudent", data.total_students ? `${data.top_student} is currently the highest performer.` : "Add student records to see the top performer.");
  setKpi("#topAverage", data.total_students ? `${Number(data.top_average).toFixed(1)}%` : "—");
  renderCharts(data);
}

function renderStudents(students) {
  const tbody = $("#studentTableBody");
  $("#recordCount").textContent = `${students.length} record${students.length === 1 ? "" : "s"}`;
  $("#tableSummary").textContent = `Showing ${students.length} student${students.length === 1 ? "" : "s"}`;

  if (!students.length) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No matching records. Add a student or change your filters.</td></tr>';
    return;
  }

  tbody.innerHTML = students.map((student) => {
    const initials = student.name.trim().split(/\s+/).slice(0, 2).map(part => part[0] || "").join("").toUpperCase();
    const resultClass = student.result === "Pass" ? "pass" : "fail";
    return `
      <tr>
        <td><div class="student-name"><span class="student-initial">${escapeHtml(initials)}</span><span><strong>${escapeHtml(student.name)}</strong><small>${escapeHtml(student.academic_year || "Academic year not set")}</small></span></div></td>
        <td>${escapeHtml(student.usn)}</td>
        <td><span class="department-chip">${escapeHtml(student.department)}</span></td>
        <td>Sem ${Number(student.semester)}</td>
        <td class="score-cell">${Number(student.average).toFixed(1)}%</td>
        <td>${Number(student.attendance).toFixed(1)}%</td>
        <td><span class="grade-chip">${escapeHtml(student.grade)}</span></td>
        <td><span class="result-chip ${resultClass}">${escapeHtml(student.result)}</span></td>
        <td><div class="row-actions"><button class="row-action" data-action="edit" data-id="${student.id}" title="Edit student" aria-label="Edit ${escapeHtml(student.name)}">✎</button><button class="row-action delete" data-action="delete" data-id="${student.id}" title="Delete student" aria-label="Delete ${escapeHtml(student.name)}">⌫</button></div></td>
      </tr>`;
  }).join("");
}

async function loadStudents() {
  const values = { ...currentFilters(), search: $("#studentSearch").value.trim() };
  const students = await apiRequest(`/api/students?${queryString(values)}`);
  renderStudents(students);
}

async function loadFilters() {
  const currentDepartment = $("#departmentFilter").value;
  const currentSemester = $("#semesterFilter").value;
  const data = await apiRequest("/api/filters");
  const departmentSelect = $("#departmentFilter");
  const semesterSelect = $("#semesterFilter");

  departmentSelect.innerHTML = '<option value="">All departments</option>' + data.departments.map(value => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
  semesterSelect.innerHTML = '<option value="">All semesters</option>' + data.semesters.map(value => `<option value="${Number(value)}">Semester ${Number(value)}</option>`).join("");
  departmentSelect.value = data.departments.includes(currentDepartment) ? currentDepartment : "";
  semesterSelect.value = data.semesters.map(String).includes(currentSemester) ? currentSemester : "";
}

async function refreshAll() {
  try {
    await Promise.all([loadDashboard(), loadStudents()]);
  } catch (error) {
    showToast(error.message, true);
  }
}

function openModal(student = null) {
  const modal = $("#studentModal");
  const form = $("#studentForm");
  form.reset();
  editingStudentId = student ? student.id : null;
  $("#modalTitle").textContent = student ? "Edit student details" : "Add new student";
  $("#saveStudentButton").textContent = student ? "Update student" : "Save student";
  $("#formError").textContent = "";

  if (student) {
    ["name", "usn", "department", "semester", "academic_year", "attendance", ...SUBJECT_COLUMNS].forEach((field) => {
      if (form.elements[field]) form.elements[field].value = student[field] ?? "";
    });
  }
  updateAveragePreview();
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  setTimeout(() => form.elements.name.focus(), 50);
}

function closeModal() {
  $("#studentModal").classList.remove("open");
  $("#studentModal").setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  editingStudentId = null;
}

function updateAveragePreview() {
  const form = $("#studentForm");
  const scores = SUBJECT_COLUMNS.map(column => Number(form.elements[column]?.value || 0));
  const average = scores.reduce((sum, value) => sum + value, 0) / scores.length;
  $("#averagePreview").textContent = `${average.toFixed(2)}%`;
}

function getFormPayload() {
  const form = $("#studentForm");
  const payload = {};
  ["name", "usn", "department", "semester", "academic_year", "attendance", ...SUBJECT_COLUMNS].forEach((field) => {
    payload[field] = form.elements[field].value;
  });
  return payload;
}

async function editStudent(id) {
  try {
    const students = await apiRequest(`/api/students?`);
    const student = students.find(item => Number(item.id) === Number(id));
    if (!student) throw new Error("Student record not found. Refresh and try again.");
    openModal(student);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function deleteStudent(id) {
  const confirmed = window.confirm("Delete this student record? This action cannot be undone.");
  if (!confirmed) return;
  try {
    const result = await apiRequest(`/api/students/${id}`, { method: "DELETE" });
    showToast(result.message);
    await loadFilters();
    await refreshAll();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function saveStudent(event) {
  event.preventDefault();
  const form = $("#studentForm");
  if (!form.reportValidity()) return;
  const payload = getFormPayload();
  const button = $("#saveStudentButton");
  button.disabled = true;
  button.textContent = editingStudentId ? "Updating..." : "Saving...";
  $("#formError").textContent = "";

  try {
    const url = editingStudentId ? `/api/students/${editingStudentId}` : "/api/students";
    const method = editingStudentId ? "PUT" : "POST";
    const result = await apiRequest(url, { method, body: JSON.stringify(payload) });
    closeModal();
    showToast(result.message);
    await loadFilters();
    await refreshAll();
  } catch (error) {
    $("#formError").textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = editingStudentId ? "Update student" : "Save student";
  }
}

function exportCsv() {
  const query = queryString(currentFilters());
  window.location.href = `/export/csv${query ? `?${query}` : ""}`;
}

function setupEvents() {
  $("#addStudentButton").addEventListener("click", () => openModal());
  $("#addStudentTop").addEventListener("click", (event) => { event.preventDefault(); openModal(); });
  $("#closeModal").addEventListener("click", closeModal);
  $("#cancelModal").addEventListener("click", closeModal);
  $("#studentModal").addEventListener("click", (event) => { if (event.target.id === "studentModal") closeModal(); });
  $("#studentForm").addEventListener("submit", saveStudent);
  SUBJECT_COLUMNS.forEach(column => $("#studentForm").elements[column].addEventListener("input", updateAveragePreview));
  $("#studentTableBody").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    if (button.dataset.action === "edit") editStudent(button.dataset.id);
    if (button.dataset.action === "delete") deleteStudent(button.dataset.id);
  });
  $("#departmentFilter").addEventListener("change", refreshAll);
  $("#semesterFilter").addEventListener("change", refreshAll);
  $("#studentSearch").addEventListener("input", loadStudents);
  $("#clearFilters").addEventListener("click", async () => {
    $("#departmentFilter").value = "";
    $("#semesterFilter").value = "";
    $("#studentSearch").value = "";
    await refreshAll();
  });
  $("#refreshButton").addEventListener("click", refreshAll);
  $("#exportButton").addEventListener("click", exportCsv);
  $("#mobileMenu").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
  document.querySelectorAll(".nav-link").forEach(link => link.addEventListener("click", () => $("#sidebar").classList.remove("open")));
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeModal(); });
}

async function initializeDashboard() {
  setupEvents();
  try {
    await loadFilters();
    await refreshAll();
  } catch (error) {
    showToast(error.message, true);
  }
}

document.addEventListener("DOMContentLoaded", initializeDashboard);
