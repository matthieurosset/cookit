/* Cookit - Minimal JS for dynamic form rows and cook mode */

function addIngredientRow() {
    const container = document.getElementById('ingredients-container');
    const row = document.createElement('div');
    row.className = 'ingredient-row';
    row.innerHTML = `
        <input type="text" name="ing_qty" placeholder="Qté" class="input-sm">
        <input type="text" name="ing_unit" placeholder="Unité" class="input-sm">
        <input type="text" name="ing_name" placeholder="Ingrédient" required class="input-grow">
        <button type="button" class="btn btn-icon btn-remove-row" onclick="removeRow(this)" title="Supprimer"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4h12M5.33 4V2.67a1.33 1.33 0 011.34-1.34h2.66a1.33 1.33 0 011.34 1.34V4M13 4v9.33a1.33 1.33 0 01-1.33 1.34H4.33A1.33 1.33 0 013 13.33V4"/></svg></button>
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
        <button type="button" class="btn btn-icon btn-remove-row" onclick="removeRow(this)" title="Supprimer"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4h12M5.33 4V2.67a1.33 1.33 0 011.34-1.34h2.66a1.33 1.33 0 011.34 1.34V4M13 4v9.33a1.33 1.33 0 01-1.33 1.34H4.33A1.33 1.33 0 013 13.33V4"/></svg></button>
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

// --- Shopping quantity controls ---
function syncQtyUnit() {
    const raw = (document.getElementById('input-qty-unit').value || '').trim();
    const hiddenQty = document.getElementById('hidden-qty');
    const hiddenUnit = document.getElementById('hidden-unit');
    if (!hiddenQty) return;
    if (!raw) {
        hiddenQty.value = '';
        hiddenUnit.value = '';
        return;
    }
    const match = raw.match(/^(\d+(?:[.,]\d+)?)\s*([a-zA-Zàéèêëïôùûüçæœ]*)$/);
    if (match) {
        hiddenQty.value = match[1].replace(',', '.');
        hiddenUnit.value = match[2] || '';
    } else {
        hiddenQty.value = '';
        hiddenUnit.value = '';
    }
}

function adjustQty(delta) {
    const input = document.getElementById('input-qty-unit');
    if (!input) return;
    const raw = (input.value || '').trim();
    const match = raw.match(/^(\d+(?:[.,]\d+)?)\s*([a-zA-Zàéèêëïôùûüçæœ]*)$/);
    let num = 0;
    let unit = '';
    if (match) {
        num = parseFloat(match[1].replace(',', '.')) || 0;
        unit = match[2] || '';
    }
    num = Math.max(0, num + delta);
    if (num === 0) {
        input.value = '';
    } else {
        const numStr = Number.isInteger(num) ? num : num.toFixed(1);
        input.value = unit ? numStr + ' ' + unit : '' + numStr;
    }
    syncQtyUnit();
}

function adjustPortions(delta) {
    const input = document.getElementById('input-portions');
    if (!input) return;
    let val = parseInt(input.value) || 1;
    val = Math.max(1, val + delta);
    input.value = val;
}

// --- Recipe modal ---
function openRecipeModal() {
    document.getElementById('recipe-modal').classList.add('open');
}

function closeRecipeModal() {
    const modal = document.getElementById('recipe-modal');
    if (!modal) return;
    modal.classList.remove('open');
    const form = modal.querySelector('form');
    if (form) form.reset();
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeRecipeModal();
});

// --- Shopping autocomplete & frequent items ---
(function() {
    let debounceTimer;
    let activeIndex = -1;

    document.addEventListener('DOMContentLoaded', () => {
        const nameInput = document.getElementById('input-name');
        if (!nameInput) return;

        const dropdown = document.getElementById('autocomplete-dropdown');
        const qtyUnitInput = document.getElementById('input-qty-unit');
        const form = document.getElementById('add-item-form');

        // Autocomplete on typing
        nameInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const q = nameInput.value.trim();
            if (q.length < 2) {
                dropdown.classList.remove('show');
                return;
            }
            debounceTimer = setTimeout(() => {
                fetch('/courses/suggestions?q=' + encodeURIComponent(q))
                    .then(r => r.json())
                    .then(items => {
                        if (!items.length) {
                            dropdown.classList.remove('show');
                            return;
                        }
                        activeIndex = -1;
                        dropdown.innerHTML = items.map((item, i) =>
                            `<div class="autocomplete-item" data-index="${i}"
                                  data-name="${item.name}"
                                  data-quantity="${item.quantity}"
                                  data-unit="${item.unit}">
                                <span class="ac-name">${item.name}</span>
                                ${item.quantity || item.unit ?
                                    `<span class="ac-meta">${item.quantity} ${item.unit}</span>` : ''}
                            </div>`
                        ).join('');
                        dropdown.classList.add('show');
                    });
            }, 200);
        });

        // Click suggestion
        dropdown.addEventListener('mousedown', (e) => {
            const item = e.target.closest('.autocomplete-item');
            if (!item) return;
            e.preventDefault();
            selectSuggestion(item, nameInput, qtyUnitInput, dropdown);
        });

        // Keyboard navigation
        nameInput.addEventListener('keydown', (e) => {
            if (!dropdown.classList.contains('show')) return;
            const items = dropdown.querySelectorAll('.autocomplete-item');
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                activeIndex = Math.min(activeIndex + 1, items.length - 1);
                updateActive(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                activeIndex = Math.max(activeIndex - 1, -1);
                updateActive(items);
            } else if (e.key === 'Enter' && activeIndex >= 0) {
                e.preventDefault();
                selectSuggestion(items[activeIndex], nameInput, qtyUnitInput, dropdown);
            } else if (e.key === 'Escape') {
                dropdown.classList.remove('show');
            }
        });

        // Close on blur
        nameInput.addEventListener('blur', () => {
            setTimeout(() => dropdown.classList.remove('show'), 150);
        });

        // Frequent item buttons
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.frequent-btn');
            if (!btn) return;
            nameInput.value = btn.dataset.name;
            const q = btn.dataset.quantity || '';
            const u = btn.dataset.unit || '';
            qtyUnitInput.value = q ? q + u : '';
            syncQtyUnit();
            htmx.trigger(form, 'submit');
        });
    });

    function selectSuggestion(item, nameInput, qtyUnitInput, dropdown) {
        nameInput.value = item.dataset.name;
        const q = item.dataset.quantity || '';
        const u = item.dataset.unit || '';
        qtyUnitInput.value = q ? q + u : '';
        syncQtyUnit();
        dropdown.classList.remove('show');
        nameInput.focus();
    }

    function updateActive(items) {
        items.forEach((el, i) => {
            el.classList.toggle('active', i === activeIndex);
        });
    }
})();

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
