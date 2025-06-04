document.addEventListener("DOMContentLoaded", () => {
    const csrf = Cookies.get('csrftoken');
    
    // Базовые настройки цвета для всех страниц
    if (document.querySelector("#bg-color")) {
        document.body.style.backgroundColor = document.querySelector("#bg-color").innerHTML;
        document.body.style.color = document.querySelector("#text-color").innerHTML;
        document.querySelectorAll(".txt-clr").forEach(element => {
            element.style.color = document.querySelector("#text-color").innerHTML;
        });
    }

    // Обработка заголовка и описания формы
    document.querySelectorAll(".input-form-title").forEach(title => {
        title.addEventListener("input", function(){
            fetch(`edit_title`, {
                method: "POST",
                headers: {'X-CSRFToken': csrf},
                body: JSON.stringify({
                    "title": this.value
                })
            });
            document.title = `${this.value} - Medical Forms`;
            document.querySelectorAll(".input-form-title").forEach(ele => {
                ele.value = this.value;
            });
        });
    });

    // Обработка описания формы
    const descriptionInput = document.querySelector("#input-form-description");
    if (descriptionInput) {
        descriptionInput.addEventListener("input", function(){
            fetch('edit_description', {
                method: "POST",
                headers: {'X-CSRFToken': csrf},
                body: JSON.stringify({
                    "description": this.value
                })
            });
        });
    }

    // Обработка textarea для автоматической высоты
    document.querySelectorAll(".textarea-adjust").forEach(tx => {
        tx.style.height = "auto";
        tx.style.height = (10 + tx.scrollHeight)+"px";
        tx.addEventListener('input', e => {
            tx.style.height = "auto";
            tx.style.height = (10 + tx.scrollHeight)+"px";
        });
    });

    // Обработка настроек формы на отдельной странице
    if (document.querySelector("#setting-form")) {
        // Обработчики для всех чекбоксов настроек
        const settingCheckboxes = [
            'collect_email',
            'authenticated_responder',
            'edit_after_submit',
            'allow_view_score',
            'limit_ip',
            'submit_limit',
            'is_single_form',
            'is_active'
        ];

        // Добавляем обработчики изменений для каждого чекбокса
        settingCheckboxes.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.addEventListener('change', function() {
                    const data = {};
                    data[id] = this.checked;
                    
                    fetch('edit_setting', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrf,
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message === "Success") {
                            console.log(`Setting ${id} updated successfully`);
                        } else {
                            console.log(`Failed to update setting ${id}`);
                            // Возвращаем предыдущее состояние при ошибке
                            this.checked = !this.checked;
                        }
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                        // Возвращаем предыдущее состояние при ошибке
                        this.checked = !this.checked;
                    });
                });
            }
        });

        // Обработчик для текстового поля сообщения подтверждения
        const confirmationMessage = document.getElementById('comfirmation_message');
        if (confirmationMessage) {
            confirmationMessage.addEventListener('input', function() {
                fetch('edit_setting', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf,
                    },
                    body: JSON.stringify({
                        confirmation_message: this.value
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message === "Success") {
                        console.log("Confirmation message updated successfully");
                    } else {
                        console.log("Failed to update confirmation message");
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        }

        // Обработчик формы настроек
        document.querySelector("#setting-form").addEventListener("submit", e => {
            e.preventDefault();
            const formData = {};
            
            // Собираем все значения с формы
            settingCheckboxes.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    formData[id] = element.checked;
                }
            });
            
            // Добавляем сообщение подтверждения
            if (confirmationMessage) {
                formData.confirmation_message = confirmationMessage.value;
            }

            fetch('edit_setting', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = document.referrer || '/';
                } else {
                    throw new Error('Failed to save settings');
                }
            })
            .catch(error => {
                console.error('Error saving settings:', error);
                alert('Произошла ошибка при сохранении настроек');
            });
        });

        // Обработчик удаления формы
        document.querySelector("#delete-form")?.addEventListener("submit", e => {
            e.preventDefault();
            if(window.confirm("Вы уверены? Это действие НЕЛЬЗЯ отменить.")){
                fetch('delete', {
                    method: "DELETE",
                    headers: {'X-CSRFToken': csrf}
                })
                .then(response => {
                    if (response.ok) {
                        window.location = "/";
                    } else {
                        throw new Error('Failed to delete form');
                    }
                })
                .catch(error => {
                    console.error('Error deleting form:', error);
                    alert('Произошла ошибка при удалении формы');
                });
            }
        });
    }

    document.querySelectorAll(".input-form-title").forEach(title => {
        title.addEventListener("input", function(){
            fetch(`edit_title`, {
                method: "POST",
                headers: {'X-CSRFToken': csrf},
                body: JSON.stringify({
                    "title": this.value
                })

            })
            document.title = `${this.value} - Medical Forms`
            document.querySelectorAll(".input-form-title").forEach(ele => {
                ele.value = this.value;
            })
        })
    })
    document.querySelector("#input-form-description")?.addEventListener("input", function(){
        fetch('edit_description', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "description": this.value
            })
        })
    })
    document.querySelectorAll(".textarea-adjust").forEach(tx => {
        tx.style.height = "auto";
        tx.style.height = (10 + tx.scrollHeight)+"px";
        tx.addEventListener('input', e => {
            tx.style.height = "auto";
            tx.style.height = (10 + tx.scrollHeight)+"px";
        })
    })
    document.querySelector("#customize-theme-btn")?.addEventListener('click', () => {
        document.querySelector("#customize-theme").style.display = "block";
        document.querySelector("#close-customize-theme").addEventListener('click', () => {
            document.querySelector("#customize-theme").style.display = "none";
        })
        window.onclick = e => {
            if(e.target == document.querySelector("#customize-theme")) document.querySelector("#customize-theme").style.display = "none";
        }
    })
    document.querySelector("#input-bg-color")?.addEventListener("input", function(){
        document.body.style.backgroundColor = this.value;
        fetch('edit_background_color', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "bgColor": this.value
            })
        })
    })
    document.querySelector("#input-text-color")?.addEventListener("input", function(){
        document.querySelectorAll(".txt-clr").forEach(element => {
            element.style.color = this.value;
        })
        fetch('edit_text_color', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "textColor": this.value
            })
        })
    })
    document.querySelectorAll(".open-setting").forEach(ele => {
        const settingElement = document.querySelector("#setting");
        const closeSettingElement = document.querySelector("#close-setting");
        
        if (settingElement && closeSettingElement) {
            ele.addEventListener('click', () => {
                settingElement.style.display = "block";
            });
            closeSettingElement.addEventListener('click', () => {
                settingElement.style.display = "none";
            });
            window.onclick = e => {
                if(e.target == settingElement) settingElement.style.display = "none";
            };
        }
    });
    document.querySelectorAll("#send-form-btn").forEach(btn => {
        const sendForm = document.querySelector("#send-form");
        const closeSendForm = document.querySelector("#close-send-form");
        
        if (sendForm && closeSendForm) {
            btn.addEventListener("click", () => {
                sendForm.style.display = "block";
            });
            closeSendForm.addEventListener("click", () => {
                sendForm.style.display = "none";
            });
            window.onclick = e => {
                if(e.target == sendForm) sendForm.style.display = "none";
            };
        }
    });
    document.querySelectorAll("[copy-btn]").forEach(btn => {
        const copyUrl = document.getElementById("copy-url");
        if (copyUrl) {
            btn.addEventListener("click", () => {
                navigator.clipboard.writeText(copyUrl.value).then(() => {
                    btn.textContent = "Скопировано!";
                    setTimeout(() => {
                        btn.textContent = "Копировать";
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                });
            });
        }
    });
    document.querySelectorAll("[copy-code-btn]").forEach(btn => {
        const copyCodeUrl = document.getElementById("copy-code-url");
        if (copyCodeUrl) {
            btn.addEventListener("click", () => {
                navigator.clipboard.writeText(copyCodeUrl.value).then(() => {
                    btn.textContent = "Скопировано!";
                    setTimeout(() => {
                        btn.textContent = "Копировать";
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                });
            });
        }
    });
    document.querySelector("#setting-form")?.addEventListener("submit", e => {
        e.preventDefault();
        fetch('edit_setting', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "collect_email": document.querySelector("#collect_email")?.checked || false,
                "authenticated_responder": document.querySelector("#authenticated_responder")?.checked || false,
                "confirmation_message": document.querySelector("#comfirmation_message")?.value || "",
                "edit_after_submit": document.querySelector("#edit_after_submit")?.checked || false,
                "allow_view_score": document.querySelector("#allow_view_score")?.checked || false,
                "limit_ip": document.querySelector("#limit_ip")?.checked || false,
                "submit_limit": document.querySelector("#submit_limit")?.checked || false,
                "is_single_form": document.querySelector("#is_single_form")?.checked || false,
                "is_active": document.querySelector("#is_active")?.checked || false
            })
        })
        .then(response => {
            if (response.ok) {
                window.location.href = document.referrer || '/';
            }
        });
    });
    document.querySelector("#delete-form")?.addEventListener("submit", e => {
        e.preventDefault();
        if(window.confirm("Вы уверены? Это действие НЕЛЬЗЯ отменить.")){
            fetch('delete', {
                method: "DELETE",
                headers: {'X-CSRFToken': csrf}
            })
            .then(() => window.location = "/")
        }
    });
    ['limit_ip', 'submit_limit', 'is_single_form', 'is_active'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', function() {
            const data = {};
            data[id] = this.checked;
            
            fetch('edit_setting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf,
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === "Success") {
                    console.log("Setting updated successfully");
                } else {
                    console.log("Failed to update setting");
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    });
    const editQuestion = () => {
        document.querySelectorAll(".input-question").forEach(question => {
            question.addEventListener('input', function(){
                let question_type;
                let required;
                let is_list;
                let is_skip;
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value
                })
                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                })
                document.querySelectorAll('.islist-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_list = rc.checked;
                })
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: this.value,
                        question_type: question_type,
                        required: required,
                        is_list: is_list,
                        is_skip: is_skip
                    })
                })
            })
        })
    }
    editQuestion();
    
    const editRequire = () => {
        document.querySelectorAll(".required-checkbox").forEach(checkbox => {
            checkbox.addEventListener('input', function(){
                let question;
                let question_type;
                let is_list;
                let is_skip;
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value
                })
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value
                })
                document.querySelectorAll('.islist-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_list = rc.checked;
                })
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: question_type,
                        required: this.checked,
                        is_list: is_list,
                        is_skip: is_skip
                    })
                })
            })
        })
    }
    editRequire()
    const editList = () => {
        document.querySelectorAll(".islist-checkbox").forEach(checkbox => {
            checkbox.addEventListener('input', function(){
                let question;
                let question_type;
                let required;
                let is_skip;
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value;
                });
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value;
                });
                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                })
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: question_type,
                        is_list: this.checked,
                        required: required,
                        is_skip: is_skip
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Edit question response:', data);
                })
                .catch(error => {
                    console.error('Error editing question:', error);
                });
            });
        });
    };
    editList();
    const editSkip = () => {
        document.querySelectorAll(".isskip-checkbox").forEach(checkbox => {
            checkbox.addEventListener('input', function(){
                let question;
                let question_type;
                let required;
                let is_list;
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value;
                });
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value;
                });
                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                })
                document.querySelectorAll('.islist-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_list = rc.checked;
                })
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: question_type,
                        is_skip: this.checked,
                        required: required,
                        is_list: is_list
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Edit question response:', data);
                })
                .catch(error => {
                    console.error('Error editing question:', error);
                });
            });
        });
    };
    editSkip();
    const editChoice = () => {
        document.querySelectorAll(".edit-choice").forEach(choice => {
            choice.addEventListener("input", function(){
                fetch('edit_choice', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        "id": this.dataset.id,
                        "choice": this.value
                    })
                })
            })
        })
    }
    editChoice()
    const removeOption = () => {
        document.querySelectorAll(".remove-option").forEach(ele => {
            ele.addEventListener("click",function(){
                fetch('remove_choice', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        "id": this.dataset.id
                    })
                })
                .then(() => {
                    this.parentNode.parentNode.removeChild(this.parentNode)
                })
            })
        })
    }
    removeOption()
    const addOption = () => {
        document.querySelectorAll(".add-option").forEach(question => {
            // Удаляем существующие обработчики перед добавлением нового
            const clonedQuestion = question.cloneNode(true);
            question.parentNode.replaceChild(clonedQuestion, question);
            
            clonedQuestion.addEventListener("click", function(){
                fetch('add_choice', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        "question": this.dataset.question
                    })
                })
                .then(response => response.json())
                .then(result => {
                    let element = document.createElement("div");
                    element.classList.add('choice');
                    if(this.dataset.type === "multiple choice"){
                        element.innerHTML = `<input type="radio" id="${result["id"]}" disabled>
                        <label for="${result["id"]}">
                            <input type="text" value="${result["choice"]}" class="edit-choice" data-id="${result["id"]}">
                        </label>
                        <span class="remove-option" title = "Remove" data-id="${result["id"]}">&times;</span>`;
                    }else if(this.dataset.type === "checkbox"){
                        element.innerHTML = `<input type="checkbox" id="${result["id"]}" disabled>
                        <label for="${result["id"]}">
                            <input type="text" value="${result["choice"]}" class="edit-choice" data-id="${result["id"]}">
                        </label>
                        <span class="remove-option" title = "Remove" data-id="${result["id"]}">&times;</span>`;
                    }
                    document.querySelectorAll(".choices").forEach(choices => {
                        if(choices.dataset.id === this.dataset.question){
                            choices.insertBefore(element, choices.childNodes[choices.childNodes.length -2]);
                            editChoice();
                            removeOption();
                            // Добавляем фокус и выделение текста в новом поле
                            const newInput = element.querySelector('.edit-choice');
                            if (newInput) {
                                newInput.focus();
                                newInput.select();
                            }
                        }
                    });
                })
            })
        })
    }
    addOption()
    const deleteQuestion = () => {
        document.querySelectorAll(".delete-question").forEach(question => {
            question.addEventListener("click", function() {
                const questionId = this.dataset.id;
                fetch(`delete_question/${questionId}`, {
                    method: "DELETE",
                    headers: {
                        'X-CSRFToken': csrf,
                    }
                })
                .then(response => {
                    if (response.ok) {
                        const questionElement = document.querySelector(`.question[data-id='${questionId}']`);
                        if (questionElement) {
                            questionElement.remove();
                        }
                    } else {
                        console.error('Ошибка удаления вопроса');
                    }
                })
                .catch(error => {
                    console.error('Ошибка запроса:', error);
                });
            });
        });
    };
    
    const copyQuestion = () => {
        document.querySelectorAll(".copy-question").forEach(question => {
            question.addEventListener("click", function() {
                const questionId = this.dataset.id;
                fetch(`copy_question/${questionId}`, {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': csrf,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(result => {
                    let ele = document.createElement('div');
                    ele.classList.add('margin-top-bottom');
                    ele.classList.add('box');
                    ele.classList.add('question-box');
                    ele.classList.add('question');
                    ele.setAttribute("data-id", result["question"].id);
                    ele.setAttribute("data-order", result["question"].order);
                    
                    let choicesHtml = '';
                    if (result["question"].question_type === "multiple choice" || result["question"].question_type === "checkbox") {
                        choicesHtml = `
                            <div class="choices" data-id="${result["question"].id}">
                                ${result["choices"].map(choice => `
                                    <div class="choice">
                                        <input type="${result["question"].question_type === 'multiple choice' ? 'radio' : 'checkbox'}" id="${choice.id}" disabled>
                                        <label for="${choice.id}">
                                            <input type="text" value="${choice.choice}" class="edit-choice" data-id="${choice.id}">
                                        </label>
                                        <span class="remove-option" title="Удалить" data-id="${choice.id}">&times;</span>
                                    </div>
                                `).join('')}
                                <div class="choice">
                                    <input type="${result["question"].question_type === 'multiple choice' ? 'radio' : 'checkbox'}" disabled>
                                    <label for="add-choice" class="add-option" id="add-option" data-question="${result["question"].id}" data-type="${result["question"].question_type}"><input type="text" value="Добавить вариант" class="add-option edit-choice"></label>
                                </div>
                            </div>`;
                    } else if (result["question"].question_type === "short") {
                        choicesHtml = `
                            <div class="answers" data-id="${result["question"].id}">
                                <input type="text" class="short-answer" disabled placeholder="Строчный текст"/>
                            </div>`;
                    } else if (result["question"].question_type === "paragraph") {
                        choicesHtml = `
                            <div class="answers" data-id="${result["question"].id}">
                                <textarea class="long-answer" disabled placeholder="Абзац"></textarea>
                            </div>`;
                    } else if (result["question"].question_type === "range slider") {
                        choicesHtml = `
                            <div class="answers" data-id="${result["question"].id}">
                                <input type="range" min="0" max="100" value="50" class="slider" disabled>
                                <label for="input-max-value">
                                    <input type="number" id="input-max-value" value="${result["question"].max_value}" class="edit-choice" data-id="${result["question"].id}" placeholder="Макс. число">
                                </label>
                            </div>`;
                    }

                    ele.innerHTML = `
                        <div class="drag-handle">⋮⋮</div>
                        <input type="text" data-id="${result["question"].id}" class="question-title edit-on-click input-question" value="${result["question"].question}">
                        <select class="question-type-select input-question-type" data-id="${result["question"].id}" data-origin_type="${result["question"].question_type}">
                            // <option value="title" ${result["question"].question_type === "title" ? "selected" : ""}>Заголовок</option>
                            <option value="short" ${result["question"].question_type === "short" ? "selected" : ""}>Строка</option>
                            <option value="paragraph" ${result["question"].question_type === "paragraph" ? "selected" : ""}>Абзац</option>
                            <option value="multiple choice" ${result["question"].question_type === "multiple choice" ? "selected" : ""}>Один вариант</option>
                            <option value="checkbox" ${result["question"].question_type === "checkbox" ? "selected" : ""}>Мультивыбор</option>
                            <option value="range slider" ${result["question"].question_type === "range slider" ? "selected" : ""}>Ползунок</option>
                        </select>
                        ${choicesHtml}
                        <div class="choice-option">
                            <div>
                                <label class="toggle-switch" for="required-${result["question"].id}">
                                    <input type="checkbox" class="required-checkbox" id="required-${result["question"].id}" 
                                           data-id="${result["question"].id}" ${result["question"].required ? "checked" : ""}>
                                    <span class="toggle-slider"></span>
                                </label>
                                <label for="required-${result["question"].id}" class="required">Обязателен*</label>
                            </div>
                            <div class="float-right">
                                <a alt="Copy question icon" class="question-option-icon copy-question" title="Копировать вопрос"
                                   data-id="${result["question"].id}">
                                    <i class="bi bi-copy copy-question question-icon"></i>
                                </a>
                                <a alt="Delete question icon" class="question-option-icon delete-question" title="Удалить поле"
                                   data-id="${result["question"].id}">
                                    <i class="bi bi-trash-fill delete-question question-icon"></i>
                                </a>
                            </div>
                            <div>
                                <label class="toggle-switch" for="isskip-${result["question"].id}">
                                    <input type="checkbox" class="isskip-checkbox" id="isskip-${result["question"].id}" 
                                           data-id="${result["question"].id}" ${result["question"].is_skip ? "checked" : ""}>
                                    <span class="toggle-slider"></span>
                                </label>
                                <label for="isskip-${result["question"].id}" class="required">Необязателен для статистики</label>
                            </div>
                            ${result["question"].question_type === "multiple choice" ? `
                                <div>
                                    <label class="toggle-switch" for="list-${result["question"].id}">
                                        <input type="checkbox" class="islist-checkbox" id="list-${result["question"].id}" 
                                               data-id="${result["question"].id}" ${result["question"].is_list ? "checked" : ""}>
                                        <span class="toggle-slider"></span>
                                    </label>
                                    <label for="list-${result["question"].id}" class="is_list">Список</label>
                                </div>
                            ` : ''}
                            ${(result["question"].question_type === "short" || result["question"].question_type === "paragraph") ? `
                                <div>
                                    <label class="toggle-switch" for="isnegative-${result["question"].id}">
                                        <input type="checkbox" class="isnegative-checkbox" id="isnegative-${result["question"].id}" 
                                               data-id="${result["question"].id}" ${result["question"].is_negative ? "checked" : ""}>
                                        <span class="toggle-slider"></span>
                                    </label>
                                    <label for="isnegative-${result["question"].id}" class="required">Негативный отзыв</label>
                                </div>
                            ` : ''}
                        </div>
                        <div class="drag-handle">⋮⋮</div>`;

                    document.querySelector("#questions-container").appendChild(ele);
                    
                    // Переинициализируем все обработчики
                    editChoice();
                    removeOption();
                    changeType();
                    editQuestion();
                    editRequire();
                    editList();
                    editSkip();
                    addOption();
                    deleteQuestion();
                    copyQuestion();
                    initMaxValueHandlers();
                    initQuestionBoxes();
                })
                .catch(error => {
                    console.error('Ошибка копирования вопроса:', error);
                });
            });
        });
    };
    
    deleteQuestion();
    copyQuestion();
    const changeType = () => {
        document.querySelectorAll(".input-question-type").forEach(ele => {
            ele.addEventListener('input', function(){
                const questionId = this.dataset.id;
                const questionBox = this.closest('.question');
                const question = questionBox.querySelector('.input-question').value;
                const required = questionBox.querySelector('.required-checkbox').checked;
                const is_list = questionBox.querySelector('.islist-checkbox')?.checked || false;
                const is_skip = questionBox.querySelector('.isskip-checkbox').checked;
                const max_value = questionBox.querySelector('#input-max-value')?.value || 100;

                // Удаляем старый контейнер с вариантами ответов, если он есть
                const oldChoicesContainer = questionBox.querySelector('.choices');
                if (oldChoicesContainer) {
                    oldChoicesContainer.remove();
                }

                // Удаляем старый контейнер с ответами, если он есть
                const oldAnswersContainer = questionBox.querySelector('.answers');
                if (oldAnswersContainer) {
                    oldAnswersContainer.remove();
                }

                // Создаем новый контейнер в зависимости от типа вопроса
                let newContainer = '';
                if (this.value === 'multiple choice' || this.value === 'checkbox') {
                    // Сначала создаем базовый контейнер
                    newContainer = `
                        <div class="choices" data-id="${questionId}">
                            <div class="choice">
                                <input type="${this.value === 'multiple choice' ? 'radio' : 'checkbox'}" disabled>
                                <label>
                                    <input type="text" value="Вариант 1" class="edit-choice" disabled>
                                </label>
                            </div>
                            <div class="choice">
                                <input type="${this.value === 'multiple choice' ? 'radio' : 'checkbox'}" disabled>
                                <label for="add-choice" class="add-option" id="add-option" data-question="${questionId}" data-type="${this.value}">
                                    <input type="text" value="Добавить вариант" class="add-option edit-choice">
                                </label>
                            </div>
                        </div>
                    `;
                } else if (this.value === 'short') {
                    newContainer = `
                        <div class="answers" data-id="${questionId}">
                            <input type="text" class="short-answer" disabled placeholder="Строчный текст"/>
                        </div>
                    `;
                } else if (this.value === 'paragraph') {
                    newContainer = `
                        <div class="answers" data-id="${questionId}">
                            <textarea class="long-answer" disabled placeholder="Абзац"></textarea>
                        </div>
                    `;
                } else if (this.value === 'range slider') {
                    newContainer = `
                        <div class="answers" data-id="${questionId}">
                            <input type="range" min="0" max="100" value="50" class="slider" disabled>
                            <label for="input-max-value">
                                <input type="number" id="input-max-value" value="100" class="edit-choice" data-id="${questionId}" placeholder="Макс. число">
                            </label>
                        </div>`;
                }

                // Вставляем новый контейнер после select
                if (newContainer) {
                    this.insertAdjacentHTML('afterend', newContainer);
                }

                // Обновляем опции в зависимости от типа
                const choiceOption = questionBox.querySelector('.choice-option');
                const isListOption = choiceOption.querySelector('.islist-checkbox')?.parentElement.parentElement;
                const isNegativeOption = choiceOption.querySelector('.isnegative-checkbox')?.parentElement.parentElement;

                // Показываем/скрываем опцию "Список" только для multiple choice
                if (isListOption) {
                    isListOption.style.display = this.value === 'multiple choice' ? '' : 'none';
                }

                // Показываем/скрываем опцию "Негативный отзыв" только для short и paragraph
                if (isNegativeOption) {
                    isNegativeOption.style.display = (this.value === 'short' || this.value === 'paragraph') ? '' : 'none';
                }

                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: this.value,
                        required: required,
                        is_list: is_list,
                        is_skip: is_skip,
                        is_negative: false
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(() => {
                    // Если тип изменен на multiple choice или checkbox, создаем первый вариант
                    if (this.value === 'multiple choice' || this.value === 'checkbox') {
                        return fetch('add_choice', {
                            method: "POST",
                            headers: {'X-CSRFToken': csrf},
                            body: JSON.stringify({
                                "question": this.dataset.id
                            })
                        });
                    }
                    if (this.value === 'range slider') {
                        return fetch(`/update_max_value/${this.dataset.id}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrf,
                            },
                            body: JSON.stringify({ max_value: max_value })
                        });
                    }
                })
                .then(response => {
                    if (response) {
                        return response.json();
                    }
                })
                .then(result => {
                    if (result && (this.value === 'multiple choice' || this.value === 'checkbox')) {
                        // Обновляем первый вариант с реальными данными
                        const choicesContainer = questionBox.querySelector('.choices');
                        const firstChoice = choicesContainer.querySelector('.choice');
                        firstChoice.innerHTML = `
                            <input type="${this.value === 'multiple choice' ? 'radio' : 'checkbox'}" id="${result.id}" disabled>
                            <label for="${result.id}">
                                <input type="text" value="${result.choice}" class="edit-choice" data-id="${result.id}">
                            </label>
                            <span class="remove-option" title="Удалить" data-id="${result.id}">&times;</span>
                        `;
                        
                        // Переинициализируем обработчики
                        editChoice();
                        removeOption();
                        addOption();
                        initQuestionBoxes();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    localStorage.removeItem('scrollPosition');
                    alert('Произошла ошибка при изменении типа вопроса. Пожалуйста, попробуйте еще раз.');
                });
            });
        });
    };
    changeType();
    document.querySelector("#add-question").addEventListener("click", () => {
        fetch('add_question', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(result => {
            let ele = document.createElement('div');
            ele.classList.add('margin-top-bottom');
            ele.classList.add('box');
            ele.classList.add('question-box');
            ele.classList.add('question');
            ele.setAttribute("data-id", result.question.id);
            ele.setAttribute("data-order", result.question.order);
            
            let choicesHtml = '';
            if (result.question.question_type === "multiple choice" || result.question.question_type === "checkbox") {
                choicesHtml = `
                    <div class="choices" data-id="${result.question.id}">
                        ${result.choices.map(choice => `
                            <div class="choice">
                                <input type="${result.question.question_type === 'multiple choice' ? 'radio' : 'checkbox'}" id="${choice.id}" disabled>
                                <label for="${choice.id}">
                                    <input type="text" value="${choice.choice}" class="edit-choice" data-id="${choice.id}">
                                </label>
                                <span class="remove-option" title="Удалить" data-id="${choice.id}">&times;</span>
                            </div>
                        `).join('')}
                        <div class="choice">
                            <input type="${result.question.question_type === 'multiple choice' ? 'radio' : 'checkbox'}" disabled>
                            <label for="add-choice" class="add-option" id="add-option" data-question="${result.question.id}" data-type="${result.question.question_type}">
                                <input type="text" value="Добавить вариант" class="add-option edit-choice">
                            </label>
                        </div>
                    </div>`;
            } else if (result.question.question_type === "short") {
                choicesHtml = `
                    <div class="answers" data-id="${result.question.id}">
                        <input type="text" class="short-answer" disabled placeholder="Строчный текст"/>
                    </div>`;
            } else if (result.question.question_type === "paragraph") {
                choicesHtml = `
                    <div class="answers" data-id="${result.question.id}">
                        <textarea class="long-answer" disabled placeholder="Абзац"></textarea>
                    </div>`;
            } else if (result.question.question_type === "range slider") {
                choicesHtml = `
                    <div class="answers" data-id="${result.question.id}">
                        <input type="range" min="0" max="100" value="50" class="slider" disabled>
                        <label for="input-max-value">
                            <input type="number" id="input-max-value" value="${result.question.max_value}" class="edit-choice" data-id="${result.question.id}" placeholder="Макс. число">
                        </label>
                    </div>`;
            }

            ele.innerHTML = `
                <div class="drag-handle">⋮⋮</div>
                <input type="text" data-id="${result.question.id}" class="question-title edit-on-click input-question" value="${result.question.question}">
                <select class="question-type-select input-question-type" data-id="${result.question.id}" data-origin_type="${result.question.question_type}">
                    // <option value="title" ${result.question.question_type === "title" ? "selected" : ""}>Заголовок</option>
                    <option value="short" ${result.question.question_type === "short" ? "selected" : ""}>Строка</option>
                    <option value="paragraph" ${result.question.question_type === "paragraph" ? "selected" : ""}>Абзац</option>
                    <option value="multiple choice" ${result.question.question_type === "multiple choice" ? "selected" : ""}>Один вариант</option>
                    <option value="checkbox" ${result.question.question_type === "checkbox" ? "selected" : ""}>Мультивыбор</option>
                    <option value="range slider" ${result.question.question_type === "range slider" ? "selected" : ""}>Ползунок</option>
                </select>
                ${choicesHtml}
                <div class="choice-option">
                    <div>
                        <label class="toggle-switch" for="required-${result.question.id}">
                            <input type="checkbox" class="required-checkbox" id="required-${result.question.id}" 
                                   data-id="${result.question.id}" ${result.question.required ? "checked" : ""}>
                            <span class="toggle-slider"></span>
                        </label>
                        <label for="required-${result.question.id}" class="required">Обязателен*</label>
                    </div>
                    <div class="float-right">
                        <a alt="Copy question icon" class="question-option-icon copy-question" title="Копировать вопрос"
                           data-id="${result.question.id}">
                            <i class="bi bi-copy copy-question question-icon"></i>
                        </a>
                        <a alt="Delete question icon" class="question-option-icon delete-question" title="Удалить поле"
                           data-id="${result.question.id}">
                            <i class="bi bi-trash-fill delete-question question-icon"></i>
                        </a>
                    </div>
                    <div>
                        <label class="toggle-switch" for="isskip-${result.question.id}">
                            <input type="checkbox" class="isskip-checkbox" id="isskip-${result.question.id}" 
                                   data-id="${result.question.id}" ${result.question.is_skip ? "checked" : ""}>
                            <span class="toggle-slider"></span>
                        </label>
                        <label for="isskip-${result.question.id}" class="required">Необязателен для статистики</label>
                    </div>
                    ${result.question.question_type === "multiple choice" ? `
                        <div>
                            <label class="toggle-switch" for="list-${result.question.id}">
                                <input type="checkbox" class="islist-checkbox" id="list-${result.question.id}" 
                                       data-id="${result.question.id}" ${result.question.is_list ? "checked" : ""}>
                                <span class="toggle-slider"></span>
                            </label>
                            <label for="list-${result.question.id}" class="is_list">Список</label>
                        </div>
                    ` : ''}
                    ${(result.question.question_type === "short" || result.question.question_type === "paragraph") ? `
                        <div>
                            <label class="toggle-switch" for="isnegative-${result.question.id}">
                                <input type="checkbox" class="isnegative-checkbox" id="isnegative-${result.question.id}" 
                                       data-id="${result.question.id}" ${result.question.is_negative ? "checked" : ""}>
                                <span class="toggle-slider"></span>
                            </label>
                            <label for="isnegative-${result.question.id}" class="required">Негативный отзыв</label>
                        </div>
                    ` : ''}
                </div>
                <div class="drag-handle">⋮⋮</div>`;

            document.querySelector("#questions-container").appendChild(ele);
            
            // Переинициализируем все обработчики
            editChoice();
            removeOption();
            changeType();
            editQuestion();
            editRequire();
            editList();
            editSkip();
            addOption();
            deleteQuestion();
            copyQuestion();
            initMaxValueHandlers();
            initQuestionBoxes();

            // Прокручиваем к новому вопросу
            setTimeout(() => {
                ele.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    const initMaxValueHandlers = () => {
        document.querySelectorAll('input[id="input-max-value"]').forEach(input => {
            input.addEventListener('change', function() {
                const questionId = this.getAttribute('data-id');
                const newValue = parseInt(this.value);
                
                if (isNaN(newValue) || newValue <= 0) {
                    console.error('Invalid max value');
                    return;
                }

                const slider = this.closest('.answers').querySelector('.slider');
                
                fetch(`/update_max_value/${questionId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf,
                    },
                    body: JSON.stringify({ max_value: newValue })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Max value updated successfully:', data);
                    if (slider) {
                        slider.max = newValue;
                        slider.value = Math.min(slider.value, newValue);
                    }
                })
                .catch(error => {
                    console.error('Error updating max value:', error);
                    this.value = this.defaultValue;
                });
            });
        });
    };
    initMaxValueHandlers();

    document.addEventListener('DOMContentLoaded', function() {
        const savedScrollPosition = localStorage.getItem('scrollPosition');
        if (savedScrollPosition) {
            document.querySelector('.container').scrollTop = parseInt(savedScrollPosition);
            localStorage.removeItem('scrollPosition');
        }
    });

    const editNegative = () => {
        document.querySelectorAll(".isnegative-checkbox").forEach(checkbox => {
            checkbox.addEventListener('input', function(){
                let question;
                let question_type;
                let required;
                let is_list;
                let is_skip;
                
                document.querySelectorAll(".input-question-type").forEach(qp => {
                    if(qp.dataset.id === this.dataset.id) question_type = qp.value;
                });
                document.querySelectorAll('.input-question').forEach(q => {
                    if(q.dataset.id === this.dataset.id) question = q.value;
                });
                document.querySelectorAll('.required-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) required = rc.checked;
                });
                document.querySelectorAll('.isskip-checkbox').forEach(rc => {
                    if(rc.dataset.id === this.dataset.id) is_skip = rc.checked;
                });
                
                fetch('edit_question', {
                    method: "POST",
                    headers: {'X-CSRFToken': csrf},
                    body: JSON.stringify({
                        id: this.dataset.id,
                        question: question,
                        question_type: question_type,
                        is_negative: this.checked,
                        required: required,
                        is_skip: is_skip,
                        is_list: false
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('Error editing question:', error);
                });
            });
        });
    };
    
    editNegative();

    const handleQuestionBoxClick = function(e) {
        // Игнорируем клики по кнопкам удаления и копирования
        if (e.target.closest('.delete-question') || e.target.closest('.copy-question')) {
            return;
        }

        // Если кликнули по карточке, которая уже редактируется, ничего не делаем
        if (this.classList.contains('editing')) {
            return;
        }

        // Убираем режим редактирования со всех карточек
        document.querySelectorAll('.question-box').forEach(otherBox => {
            if (otherBox !== this) {
                otherBox.classList.remove('editing');
            }
        });

        // Включаем режим редактирования для текущей карточки
        this.classList.add('editing');
    };

    const initQuestionBoxes = () => {
        document.querySelectorAll('.question-box').forEach(box => {
            // Убираем класс editing со всех карточек при инициализации
            box.classList.remove('editing');
            
            // Удаляем старый обработчик перед добавлением нового
            box.removeEventListener('click', handleQuestionBoxClick);
            box.addEventListener('click', handleQuestionBoxClick);
        });
    };

    // Инициализируем обработчики при загрузке страницы
    initQuestionBoxes();

    // Добавляем обработчик клика по документу для закрытия редактирования при клике вне карточки
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.question-box')) {
            document.querySelectorAll('.question-box').forEach(box => {
                box.classList.remove('editing');
            });
        }
    });

    // Переинициализируем обработчики после добавления новых вопросов через кнопку
    const addQuestionBtn = document.querySelector("#add-question");
    if (addQuestionBtn) {
        addQuestionBtn.addEventListener("click", () => {
            setTimeout(initQuestionBoxes, 300);
        });
    }

    // Добавляем вызов initQuestionBoxes после всех операций с вопросами
    let originalCopyQuestion = copyQuestion;
    window.copyQuestion = () => {
        originalCopyQuestion();
        setTimeout(initQuestionBoxes, 300);
    };

    let originalChangeType = changeType;
    window.changeType = () => {
        originalChangeType();
        setTimeout(initQuestionBoxes, 300);
    };
})