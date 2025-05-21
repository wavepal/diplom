document.addEventListener("DOMContentLoaded", () => {
    const csrf = Cookies.get('csrftoken');
    document.body.style.backgroundColor =  document.querySelector("#bg-color").innerHTML;
    document.body.style.color =  document.querySelector("#text-color").innerHTML;
    document.querySelectorAll(".open-setting").forEach(ele => {
        ele.addEventListener('click', () => {
            document.querySelector("#setting").style.display = "block";
        })
        document.querySelector("#close-setting").addEventListener('click', () => {
            document.querySelector("#setting").style.display = "none";
        })
        window.onclick = e => {
            if(e.target == document.querySelector("#setting")) document.querySelector("#setting").style.display = "none";
        }
    })
    document.querySelector("#delete-form").addEventListener("submit", e => {
        e.preventDefault();
        if(window.confirm("Вы уверены? Это действие нельзя отменить.")){
            fetch('delete', {
                method: "DELETE",
                headers: {'X-CSRFToken': csrf}
            })
            .then(() => window.location = "/")
        }
    })
    document.querySelectorAll("#send-form-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelector("#send-form").style.display = "block";
        })
        document.querySelector("#close-send-form").addEventListener("click", () => {
            document.querySelector("#send-form").style.display = "none";
        })
        window.onclick = e => {
            if(e.target == document.querySelector("#send-form")) document.querySelector("#send-form").style.display = "none";
        }
    })
    document.querySelectorAll("[copy-btn]").forEach(btn => {
        btn.addEventListener("click", () => {
            var url = document.getElementById("copy-url");
            navigator.clipboard.writeText(url.value).then(() => {
                document.querySelector("#send-form").style.display = "none";
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        });
    });
    document.querySelectorAll("[copy-code-btn]").forEach(btn => {
        btn.addEventListener("click", () => {
            var url = document.getElementById("copy-code-url");
            navigator.clipboard.writeText(url.value).then(() => {
                document.querySelector("#send-form").style.display = "none";
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        });
    });
    document.querySelector("#setting-form").addEventListener("submit", e => {
        e.preventDefault();
        fetch('edit_setting', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                "collect_email": document.querySelector("#collect_email").checked,
                "is_quiz": document.querySelector("#is_quiz").checked,
                "authenticated_responder": document.querySelector("#authenticated_responder").checked,
                "confirmation_message": document.querySelector("#comfirmation_message").value,
                "edit_after_submit": document.querySelector("#edit_after_submit").checked,
                "allow_view_score": document.querySelector("#allow_view_score").checked
            })
        })
        document.querySelector("#setting").style.display = "none";
        if(!document.querySelector("#collect_email").checked){
            if(document.querySelector(".collect-email")) document.querySelector(".collect-email").parentNode.removeChild(document.querySelector(".collect-email"))
        }else{
            if(!document.querySelector(".collect-email")){
                let collect_email = document.createElement("div");
                collect_email.classList.add("collect-email")
                collect_email.innerHTML = `<h3 class="question-title">Email адрес <span class="require-star">*</span></h3>
                <input type="text" autoComplete="off" aria-label="Email адрес" disabled dir = "auto" class="require-email-edit"
                placeholder = "Email адрес" />
                <p class="collect-email-desc">Эта форма собирает адреса электронных почт.</p>`
                document.querySelector("#form-head").appendChild(collect_email)
            }
        }
        if(document.querySelector("#is_quiz").checked){
            if(!document.querySelector("#add-score")){
                let is_quiz = document.createElement('a')
                is_quiz.setAttribute("href", "score");
                is_quiz.setAttribute("id", "add-score");
                is_quiz.innerHTML = `<img src = "/static/Icon/score-form.png" id="add-score" class = "form-option-icon" title = "Добавить оценку" alt = "Score icon" />`;
                document.querySelector(".question-options").appendChild(is_quiz)
            }
            if(!document.querySelector(".score")){
                let quiz_nav = document.createElement("span");
                quiz_nav.classList.add("col-4");
                quiz_nav.classList.add("navigation");
                quiz_nav.classList.add('score');
                quiz_nav.innerHTML =   `<a href = "score" class="link">Оценка</a>`;
                [...document.querySelector(".form-navigation").children].forEach(element => {
                    element.classList.remove("col-6")
                    element.classList.add('col-4')
                })
                document.querySelector(".form-navigation").insertBefore(quiz_nav, document.querySelector(".form-navigation").childNodes[2])
            }
        }else{
            if(document.querySelector("#add-score")) document.querySelector("#add-score").parentNode.removeChild(document.querySelector("#add-score"))
            if(document.querySelector(".score")){
                [...document.querySelector(".form-navigation").children].forEach(element => {
                    element.classList.remove("col-4")
                    element.classList.add('col-6')
                })
                document.querySelector(".score").parentNode.removeChild(document.querySelector(".score"))
            }
        }
    })
    document.querySelectorAll(".textarea-adjust").forEach(tx => {
        tx.style.height = "auto";
        tx.style.height = (10 + tx.scrollHeight)+"px";
        tx.addEventListener('input', e => {
            tx.style.height = "auto";
            tx.style.height = (10 + tx.scrollHeight)+"px";
        })
    })
    if(document.querySelector("#delete-responses")){
        document.querySelector("#delete-responses").addEventListener("click", () => {
            if(window.confirm("Вы уверены? Это действие нельзя отменить.")){
                fetch('responses/delete', {
                    method: "DELETE",
                    headers: {'X-CSRFToken': csrf}
                })
                .then(() => {
                    let ele = document.createElement("div");
                    ele.classList.add('margin-top-bottom');
                    ele.classList.add('box');
                    ele.classList.add('question-box');
                    ele.innerHTML = '<h1 class="response-title">0 ответов</h1>';
                    document.querySelector("#responses").parentNode.replaceChild(ele, document.querySelector("#responses"))
                })
            }
        })
    }

    // Enable all checkboxes
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="response_ids"]');
    checkboxes.forEach(checkbox => {
        checkbox.style.pointerEvents = 'auto';
        checkbox.style.cursor = 'pointer';
        checkbox.style.opacity = '1';
        checkbox.style.position = 'relative';
        checkbox.style.zIndex = '2';
        checkbox.style.width = '18px';
        checkbox.style.height = '18px';
    });

    // Add click event listener to each checkbox
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent event bubbling
        });
    });

    // Handle delete selected responses button
    const deleteSelectedBtn = document.getElementById('delete-selected-responses');
    if (deleteSelectedBtn) {
        deleteSelectedBtn.addEventListener('click', function() {
            const selectedCheckboxes = document.querySelectorAll('input[name="response_ids"]:checked');
            const selectedResponses = Array.from(selectedCheckboxes).map(input => input.value);
            
            if (selectedResponses.length === 0) {
                alert('Пожалуйста, выберите ответы для удаления.');
                return;
            }

            if (confirm('Вы уверены, что хотите удалить выделенные ответы?')) {
                const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
                
                fetch('/delete_selected_responses/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        response_ids: selectedResponses
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // Remove deleted responses from both list and table views
                        selectedResponses.forEach(responseId => {
                            // Remove from list view
                            const listItem = document.querySelector(`p input[value="${responseId}"]`);
                            if (listItem && listItem.closest('p')) {
                                listItem.closest('p').remove();
                            }

                            // Remove from table view
                            const tableRow = document.querySelector(`tr[data-response-id="${responseId}"]`);
                            if (tableRow) {
                                tableRow.remove();
                            }
                        });

                        // Update response count in title if needed
                        const responseTitle = document.querySelector('.response-title');
                        if (responseTitle && responseTitle.textContent.includes('Список ответов')) {
                            const remainingResponses = document.querySelectorAll('input[name="response_ids"]').length;
                            if (remainingResponses === 0) {
                                responseTitle.textContent = '0 ответов';
                            }
                        }
                    } else {
                        alert('Произошла ошибка при удалении ответов.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при удалении ответов.');
                });
            }
        });
    }

    // Handle links in response list
    const responseLinks = document.querySelectorAll('.bl-link');
    responseLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Allow normal link behavior
            e.stopPropagation();
        });
    });

    // Handle paragraphs containing responses
    const responseParas = document.querySelectorAll('.modal-content p');
    responseParas.forEach(para => {
        para.addEventListener('click', function(e) {
            // If the click is directly on the paragraph (not on checkbox or link)
            if (e.target === para) {
                // Find and click the link inside this paragraph
                const link = para.querySelector('.bl-link');
                if (link) {
                    link.click();
                }
            }
        });
    });

    // Add search functionality
    const searchInput = document.getElementById('response-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const responseList = document.querySelector('.modal-content');
            
            if (responseList) {
                const responses = responseList.getElementsByTagName('p');
                Array.from(responses).forEach(response => {
                    const text = response.textContent.toLowerCase();
                    response.style.display = text.includes(searchTerm) ? 'flex' : 'none';
                });
            }
        });
    }

    // Handle delete all responses button
    const deleteAllBtn = document.getElementById('delete-responses');
    if (deleteAllBtn) {
        deleteAllBtn.addEventListener('click', function() {
            if (confirm('Вы уверены? Это действие нельзя отменить.')) {
                const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
                
                fetch('responses/delete', {
                    method: "DELETE",
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.message === "Успешно") {
                        let ele = document.createElement("div");
                        ele.classList.add('margin-top-bottom');
                        ele.classList.add('box');
                        ele.classList.add('question-box');
                        ele.innerHTML = '<h1 class="response-title">0 ответов</h1>';
                        document.querySelector("#responses").parentNode.replaceChild(ele, document.querySelector("#responses"));
                    } else {
                        throw new Error('Server returned unexpected message');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Произошла ошибка при удалении ответов.");
                });
            }
        });
    }
})