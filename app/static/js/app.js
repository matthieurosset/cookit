/* Cookit - Minimal JS for dynamic form rows and cook mode */

function addIngredientRow() {
    const container = document.getElementById('ingredients-container');
    const row = document.createElement('div');
    row.className = 'ingredient-row';
    row.innerHTML = `
        <input type="text" name="ing_qty" placeholder="Qté" class="input-sm">
        <input type="text" name="ing_unit" placeholder="Unité" class="input-sm">
        <input type="text" name="ing_name" placeholder="Ingrédient" required class="input-grow">
        <button type="button" class="btn btn-icon btn-remove-row" onclick="removeRow(this)" title="Supprimer">&times;</button>
    `;
    container.appendChild(row);
    row.querySelector('[name="ing_name"]').focus();
}

function addStepRow() {
    const container = document.getElementById('steps-container');
    const row = document.createElement('div');
    row.className = 'step-row';
    row.innerHTML = `
        <span class="step-row-number"></span>
        <textarea name="step" rows="2" required></textarea>
        <button type="button" class="btn btn-icon btn-remove-row" onclick="removeRow(this)" title="Supprimer">&times;</button>
    `;
    container.appendChild(row);
    row.querySelector('textarea').focus();
    updateStepNumbers();
}

function removeRow(button) {
    const row = button.closest('.ingredient-row, .step-row');
    const container = row.parentElement;
    if (container.children.length > 1) {
        row.remove();
        updateStepNumbers();
    }
}

function updateStepNumbers() {
    document.querySelectorAll('.step-row-number').forEach((el, i) => {
        el.textContent = i + 1;
    });
}

function toggleCookMode() {
    document.body.classList.toggle('cook-mode');
    const btn = document.querySelector('.btn-cook-mode');
    if (document.body.classList.contains('cook-mode')) {
        btn.textContent = '✕ Quitter le mode cuisine';
        document.documentElement.requestFullscreen?.().catch(() => {});
    } else {
        btn.textContent = '🧑‍🍳 Mode cuisine';
        document.exitFullscreen?.().catch(() => {});
    }
}

// Initialize step numbers on page load
document.addEventListener('DOMContentLoaded', updateStepNumbers);

// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flash').forEach(el => {
        setTimeout(() => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(-10px)';
            setTimeout(() => el.remove(), 300);
        }, 4000);
    });
});
