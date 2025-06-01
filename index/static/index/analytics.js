document.addEventListener("DOMContentLoaded", () => {
    const csrf = Cookies.get('csrftoken');
    document.body.style.backgroundColor =  document.querySelector("#bg-color").innerHTML;
    document.body.style.color =  document.querySelector("#text-color").innerHTML;

    // Initialize values in original format (not percentages)
    const initializeOriginalValues = () => {
        // For total scores
        const totalScoreElements = document.querySelectorAll('.column-total-score-percentage');
        const maxScore = document.querySelector('#maxScore') ? parseInt(document.querySelector('#maxScore').value) : 0;
        
        totalScoreElements.forEach(function (element) {
            const scoreText = element.textContent.split('/')[0].trim();
            const score = parseFloat(scoreText);
            element.dataset.rawScore = score;
            if (!isNaN(score) && score !== null) {
                element.textContent = score + ' / ' + maxScore;
                element.style.color = '';
            }
        });

        // For range slider values
        const rangeSliderElements = document.querySelectorAll('.range-slider-value');
        rangeSliderElements.forEach(function (element) {
            const value = parseFloat(element.textContent.trim());
            if (!isNaN(value) && value !== null) {
                element.textContent = value;
                element.style.color = '';
            }
        });

        // For average slider values
        const averageSliderElements = document.querySelectorAll('.average-slider-value');
        averageSliderElements.forEach(function (element) {
            const value = element.dataset.rawValue;
            if (value && value !== 'N/A') {
                element.textContent = value;
                element.style.color = '';
            }
        });
    };

    // Call initialization on page load
    initializeOriginalValues();

    // Add styles for loading indicator
    const style = document.createElement('style');
    style.textContent = `
        .loading-indicator {
            display: none;
            text-align: center;
            padding: 10px;
            font-style: italic;
            color: #666;
        }
        
        .modal-content {
            position: relative;
            min-height: 100px;
        }
        
        .modal-content p {
            margin: 8px 0;
            padding: 8px;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        
        .modal-content p:hover {
            background-color: rgba(0, 0, 0, 0.05);
        }

        .responses-table {
            max-height: 500px;
            overflow-y: auto;
            position: relative;
        }
        
        .loading-indicator td {
            text-align: center;
            padding: 10px;
            font-style: italic;
            color: #666;
            background: rgba(255, 255, 255, 0.9);
        }
        
        .responses-table table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .responses-table th {
            position: sticky;
            top: 0;
            background: white;
            z-index: 1;
        }

        .chart-filter-select {
            padding: 6px 12px;
            border-radius: 4px;
            border: 1px solid #ccc;
            background-color: #fff;
            font-size: 14px;
            cursor: pointer;
            min-width: 120px;
        }

        .chart-filter-select:focus {
            outline: none;
            border-color: #80bdff;
            box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
        }
    `;
    document.head.appendChild(style);

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

    // Lazy loading for responses
    let page = 1;
    const responsesPerPage = 20;
    let loading = false;
    let hasMoreResponses = true;
    const responseList = document.querySelector('.modal-content');
    let loadingIndicator;
    // Track loaded response IDs to prevent duplicates
    let loadedResponseIds = new Set();
    
    if (responseList) {
        loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading-indicator';
        loadingIndicator.textContent = 'Загрузка...';
        loadingIndicator.style.display = 'none';
        loadingIndicator.style.textAlign = 'center';
        loadingIndicator.style.padding = '10px';
        responseList.appendChild(loadingIndicator);
    }

    // Function to load more responses
    const loadMoreResponses = async () => {
        if (!responseList || loading || !hasMoreResponses) return;
        
        loading = true;
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        
        try {
            const response = await fetch(`responses/load?page=${page}&per_page=${responsesPerPage}`, {
                headers: {
                    'X-CSRFToken': csrf
                }
            });
            
            const data = await response.json();
            
            if (data.responses.length === 0) {
                hasMoreResponses = false;
                if (loadingIndicator) {
                    loadingIndicator.style.display = 'none';
                }
                return;
            }

            // Keep track of whether we added any new responses
            let addedNewResponses = false;

            data.responses.forEach(response => {
                // Skip if we've already loaded this response
                if (loadedResponseIds.has(response.id)) {
                    return;
                }
                
                // Mark this response as loaded
                loadedResponseIds.add(response.id);
                addedNewResponses = true;
                
                const p = document.createElement('p');
                p.innerHTML = `
                    <input type="checkbox" name="response_ids" value="${response.id}">
                    <a href="${response.url}" class="bl-link">
                        ${response.profile_image ? `<img src="${response.profile_image}" alt="Фото профиля" width="25" height="25" style="border-radius: 50%; vertical-align: middle; margin-right: 5px;">` : ''}
                        Ответ ${response.username}
                        ${response.score ? `<span>- ${response.score}</span>` : ''}
                    </a>
                `;
                responseList.insertBefore(p, loadingIndicator);
                
                // Enable the newly added checkbox
                const checkbox = p.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.style.pointerEvents = 'auto';
                    checkbox.style.cursor = 'pointer';
                    checkbox.style.opacity = '1';
                    checkbox.style.position = 'relative';
                    checkbox.style.zIndex = '2';
                    checkbox.style.width = '20px';
                    checkbox.style.height = '20px';
                    checkbox.style.flexShrink = '0';
                    checkbox.style.marginRight = '15px';
                    
                    // Add click event listener
                    checkbox.addEventListener('click', function(e) {
                        e.stopPropagation(); // Prevent event bubbling
                    });
                }
                
                // Style the link for proper alignment
                const link = p.querySelector('.bl-link');
                if (link) {
                    link.style.display = 'flex';
                    link.style.alignItems = 'center';
                    link.style.flexGrow = '1';
                    
                    // Add click event for the link
                    link.addEventListener('click', function(e) {
                        // Allow normal link behavior
                        e.stopPropagation();
                    });
                }
                
                // Add click event for the paragraph
                p.addEventListener('click', function(e) {
                    // If the click is directly on the paragraph (not on checkbox or link)
                    if (e.target === p) {
                        // Find and click the link inside this paragraph
                        const link = p.querySelector('.bl-link');
                        if (link) {
                            link.click();
                        }
                    }
                });
            });

            // Only increment the page if we actually added new responses
            if (addedNewResponses) {
                page++;
            } else if (data.has_next) {
                // If we didn't add any new responses but there are more pages, try the next page
                page++;
                // Immediately load the next page
                setTimeout(loadMoreResponses, 0);
            } else {
                // If we didn't add any new responses and there are no more pages, we're done
                hasMoreResponses = false;
            }
            
        } catch (error) {
            console.error('Error loading responses:', error);
        } finally {
            loading = false;
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        }
    };

    // Initial load
    if (responseList) {
        loadMoreResponses();

        // Infinite scroll
        responseList.addEventListener('scroll', () => {
            if (responseList.scrollHeight - responseList.scrollTop <= responseList.clientHeight + 100) {
                loadMoreResponses();
            }
        });
    }

    // Search functionality with lazy loading
    const searchInput = document.getElementById('response-search');
    let searchTimeout;

    if (searchInput && responseList) {
        // Добавляем информационный текст под полем поиска
        const searchInfo = document.createElement('div');
        searchInfo.textContent = 'Поиск работает только по именам пользователей';
        searchInfo.style.fontSize = '12px';
        searchInfo.style.color = '#666';
        searchInfo.style.fontStyle = 'italic';
        searchInfo.style.marginTop = '5px';
        searchInfo.style.marginBottom = '10px';
        searchInfo.style.paddingLeft = '10px';
        searchInput.parentNode.insertBefore(searchInfo, searchInput.nextSibling);

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.trim();
            
            searchTimeout = setTimeout(async () => {
                try {
                    // Если строка поиска пуста, перезагружаем все ответы
                    if (searchTerm === '') {
                        // Сбрасываем параметры пагинации и очищаем список
                        page = 1;
                        hasMoreResponses = true;
                        loadedResponseIds.clear(); // Clear the set of loaded response IDs
                        
                        // Очищаем существующие ответы, кроме индикатора загрузки
                        const children = Array.from(responseList.children);
                        children.forEach(child => {
                            if (child !== loadingIndicator) {
                                responseList.removeChild(child);
                            }
                        });
                        
                        // Загружаем первую страницу ответов заново
                        loadMoreResponses();
                        return;
                    }
                    
                    // Показываем индикатор загрузки для поиска
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'block';
                    }
                    
                    console.log('Поисковый запрос:', searchTerm);
                    
                    // Кодируем термин для URL с поддержкой кириллицы
                    const encodedTerm = encodeURIComponent(searchTerm);
                    console.log('Закодированный запрос:', encodedTerm);
                    
                    const response = await fetch(`responses/search?term=${encodedTerm}`, {
                        headers: {
                            'X-CSRFToken': csrf
                        }
                    });
                    
                    const data = await response.json();
                    
                    // Clear existing responses except loading indicator
                    const children = Array.from(responseList.children);
                    children.forEach(child => {
                        if (child !== loadingIndicator) {
                            responseList.removeChild(child);
                        }
                    });
                    
                    // Clear the set of loaded response IDs for the new search
                    loadedResponseIds.clear();
                    
                    data.responses.forEach(response => {
                        const p = document.createElement('p');
                        p.innerHTML = `
                            <input type="checkbox" name="response_ids" value="${response.id}">
                            <a href="${response.url}" class="bl-link">
                                ${response.profile_image ? `<img src="${response.profile_image}" alt="Фото профиля" width="25" height="25" style="border-radius: 50%; vertical-align: middle; margin-right: 5px;">` : ''}
                                Ответ ${response.username}
                                ${response.score ? `<span>- ${response.score}</span>` : ''}
                            </a>
                        `;
                        responseList.insertBefore(p, loadingIndicator);
                        
                        // Enable the newly added checkbox
                        const checkbox = p.querySelector('input[type="checkbox"]');
                        if (checkbox) {
                            checkbox.style.pointerEvents = 'auto';
                            checkbox.style.cursor = 'pointer';
                            checkbox.style.opacity = '1';
                            checkbox.style.position = 'relative';
                            checkbox.style.zIndex = '2';
                            checkbox.style.width = '20px';
                            checkbox.style.height = '20px';
                            checkbox.style.flexShrink = '0';
                            checkbox.style.marginRight = '18px';
                            
                            // Add click event listener
                            checkbox.addEventListener('click', function(e) {
                                e.stopPropagation(); // Prevent event bubbling
                            });
                        }
                        
                        // Style the link for proper alignment
                        const link = p.querySelector('.bl-link');
                        if (link) {
                            link.style.display = 'flex';
                            link.style.alignItems = 'center';
                            link.style.flexGrow = '1';
                            
                            // Add click event for the link
                            link.addEventListener('click', function(e) {
                                // Allow normal link behavior
                                e.stopPropagation();
                            });
                        }
                        
                        // Add click event for the paragraph
                        p.addEventListener('click', function(e) {
                            // If the click is directly on the paragraph (not on checkbox or link)
                            if (e.target === p) {
                                // Find and click the link inside this paragraph
                                const link = p.querySelector('.bl-link');
                                if (link) {
                                    link.click();
                                }
                            }
                        });
                    });

                    if (data.responses.length === 0) {
                        // Показываем сообщение, что ничего не найдено
                        const noResultsP = document.createElement('p');
                        noResultsP.textContent = 'Не найдено ответов с указанным именем пользователя';
                        noResultsP.style.textAlign = 'center';
                        noResultsP.style.padding = '10px';
                        noResultsP.style.fontStyle = 'italic';
                        noResultsP.style.color = '#666';
                        responseList.insertBefore(noResultsP, loadingIndicator);
                    }
                } catch (error) {
                    console.error('Error searching responses:', error);
                    // Показываем сообщение об ошибке
                    const errorP = document.createElement('p');
                    errorP.textContent = 'Ошибка при поиске ответов. Пожалуйста, попробуйте еще раз.';
                    errorP.style.textAlign = 'center';
                    errorP.style.color = 'red';
                    responseList.insertBefore(errorP, loadingIndicator);
                } finally {
                    // Скрываем индикатор загрузки в любом случае
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                }
            }, 500);
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

    // Initialize lazy loading for tables
    function initializeLazyTable(tableId, loadUrl, pageSize = 20) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const tbody = table.querySelector('tbody');
        let page = 1;
        let loading = false;
        let hasMore = true;

        // Create loading indicator
        const loadingRow = document.createElement('tr');
        loadingRow.className = 'loading-indicator';
        loadingRow.innerHTML = `<td colspan="${table.querySelectorAll('th').length}">Загрузка...</td>`;
        loadingRow.style.display = 'none';
        tbody.appendChild(loadingRow);

        async function loadMoreRows() {
            if (loading || !hasMore) return;
            
            loading = true;
            loadingRow.style.display = 'table-row';
            
            try {
                const formCode = window.location.pathname.split('/')[2]; // Get form code from URL
                const response = await fetch(`/form/${formCode}/${loadUrl}?page=${page}&per_page=${pageSize}`, {
                    method: 'GET',
                    headers: {
                        'X-CSRFToken': csrf,
                        'Accept': 'application/json'
                    },
                    credentials: 'same-origin'
                });

                if (!response.ok) {
                    if (response.status === 500) {
                        throw new Error('Internal server error occurred. Please try again later.');
                    }
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (!data.rows || data.rows.length === 0) {
                    hasMore = false;
                    loadingRow.style.display = 'none';
                    return;
                }

                // Insert new rows before loading indicator
                data.rows.forEach(rowData => {
                    const row = document.createElement('tr');
                    row.innerHTML = rowData.html;
                    tbody.insertBefore(row, loadingRow);
                });

                page++;

                // After loading rows, trigger percentage conversion for average scores
                if (tableId === 'medCenterTable') {
                    const averageSliderElements = document.querySelectorAll('.average-slider-value');
                    averageSliderElements.forEach(function (element) {
                        const value = parseFloat(element.textContent.trim());
                        if (isNaN(value)) {
                            element.textContent = 'N/A';
                            element.style.color = '';
                            return;
                        }
                        const maxRangeValue = element.closest('td').dataset.maxValue;
                        element.dataset.rawValue = value;
                        const percentage = (value / maxRangeValue) * 100;
                        element.textContent = percentage.toFixed(2) + '%';
                        element.style.color = getColorBasedOnPercentage(percentage);
                    });
                }
                
            } catch (error) {
                console.error('Error loading table data:', error);
                const errorMessage = error.message || 'An unexpected error occurred while loading data';
                loadingRow.innerHTML = `<td colspan="${table.querySelectorAll('th').length}">${errorMessage}</td>`;
                hasMore = false;
            } finally {
                loading = false;
                loadingRow.style.display = 'none';
            }
        }

        // Handle scroll within table container
        const tableContainer = table.closest('.responses-table');
        if (tableContainer) {
            let scrollTimeout;
            tableContainer.addEventListener('scroll', () => {
                if (scrollTimeout) {
                    clearTimeout(scrollTimeout);
                }
                
                scrollTimeout = setTimeout(() => {
                    const { scrollTop, scrollHeight, clientHeight } = tableContainer;
                    if (scrollHeight - scrollTop <= clientHeight + 100 && hasMore && !loading) {
                        loadMoreRows();
                    }
                }, 100);
            });
        }

        // Initial load
        loadMoreRows();
    }

    // Initialize all tables
    initializeLazyTable('responsesTable', 'responses/load_table');
    initializeLazyTable('medCenterTable', 'responses/load_med_centers');
    initializeLazyTable('totalScoresTable', 'responses/load_total_scores');

    // Вспомогательная функция для генерации цветов
    function generateColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(`hsl(${(i * 360) / count}, 70%, 50%)`);
        }
        return colors;
    }

    // Глобальный объект для хранения экземпляров графиков
    window.chartInstances = new Map();

    // Функция для проверки загрузки Chart.js
    function ensureChartJsLoaded() {
        return new Promise((resolve, reject) => {
            if (window.Chart) {
                resolve(window.Chart);
            } else {
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.min.js';
                script.onload = () => resolve(window.Chart);
                script.onerror = () => reject(new Error('Failed to load Chart.js'));
                document.head.appendChild(script);
            }
        });
    }

    // Функция для инициализации графика
    async function initializeChart(container) {
        try {
            await ensureChartJsLoaded();
            
            const chartId = container.getAttribute('id');
            const chartType = container.getAttribute('data-chart-type');
            
            // Skip processing for final scores and negative impact charts
            if (chartType === 'final-scores' || chartType === 'negative-impact') {
                return;
            }
            
            const canvas = container.querySelector('canvas');
            const questionId = chartId.replace('chartContainer', '');
            const chartTypeSelect = document.getElementById(`chartTypeSelect${questionId}`);
            const timePeriodSelect = document.getElementById(`timePeriodSelect${questionId}`);
            
            if (!canvas || window.chartInstances.has(chartId)) return;

            const ctx = canvas.getContext('2d');
            let chartData;
            let originalData;
            
            // Получаем данные в зависимости от типа графика
            if (chartType === 'range-slider') {
                const url = container.getAttribute('data-url');
                if (!url) {
                    throw new Error('URL for data loading is not specified');
                }
                
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error('Failed to load chart data');
                }
                
                const responseData = await response.json();
                
                // Extract data for this specific question
                const questionData = responseData.range_slider_data[questionId];
                if (!questionData) {
                    throw new Error('No data available for this question');
                }

                // Generate colors for each dataset
                const colors = generateColors(Object.keys(questionData.averages_by_center).length);
                
                // Store original data
                originalData = {
                    labels: questionData.months,
                    datasets: Object.entries(questionData.averages_by_center).map(([center, values], index) => ({
                        label: center,
                        data: values.map(value => {
                            if (value === null || value === undefined || value === '') {
                                return '0.00'; // Return 0% for null/empty values
                            }
                            // Always convert to percentage of max value
                            return ((value / questionData.max_value) * 100).toFixed(2);
                        }),
                        borderColor: colors[index],
                        backgroundColor: colors[index],
                        borderWidth: 2,
                        fill: false
                    }))
                };
                
                // Get initial period from select
                const initialPeriod = timePeriodSelect ? parseInt(timePeriodSelect.value) : 6;
                
                // Filter data for initial period
                chartData = {
                    labels: originalData.labels.slice(-initialPeriod),
                    datasets: originalData.datasets.map(dataset => ({
                        ...dataset,
                        data: dataset.data.slice(-initialPeriod)
                    }))
                };
                
            } else {
                // Для checkbox и multiple choice графиков
                const chartDataAttr = canvas.getAttribute('data-chart-data');
                if (chartDataAttr) {
                    try {
                        chartData = JSON.parse(chartDataAttr);
                    } catch (e) {
                        console.error('Error parsing chart data:', e);
                        throw new Error('Invalid chart data format');
                    }
                } else {
                    throw new Error('Chart data is not specified');
                }
                originalData = chartData;
            }

            if (!chartData || !chartData.datasets) {
                throw new Error('Invalid chart data format');
            }
            
            // Получаем тип графика из селектора или используем bar по умолчанию
            const initialType = chartTypeSelect ? chartTypeSelect.value : 'bar';
            
            // Update dataset styling based on chart type
            chartData.datasets = chartData.datasets.map(dataset => ({
                ...dataset,
                backgroundColor: dataset.backgroundColor,
                fill: initialType === 'bar',
                borderColor: initialType === 'line' ? dataset.backgroundColor : undefined,
                borderWidth: initialType === 'line' ? 2 : 1
            }));
            
            let chartConfig = {
                type: initialType,
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        yAxes: [{
                            display: ['bar', 'line'].includes(initialType),
                            ticks: {
                                beginAtZero: true,
                                max: chartType === 'range-slider' ? 100 : undefined,
                                callback: function(value) {
                                    return chartType === 'range-slider' ? value + '%' : value;
                                }
                            }
                        }],
                        xAxes: [{
                            display: ['bar', 'line'].includes(initialType),
                            ticks: {
                                autoSkip: false
                            }
                        }]
                    },
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem, data) {
                                const datasetLabel = data.datasets[tooltipItem.datasetIndex].label || '';
                                const label = data.labels[tooltipItem.index];
                                const value = tooltipItem.yLabel || data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                                
                                if (['pie', 'doughnut', 'polarArea'].includes(chartConfig.type)) {
                                    return `${label}: ${value}`;
                                }
                                
                                return chartType === 'range-slider' 
                                    ? `${datasetLabel}: ${value}%`
                                    : `${datasetLabel}: ${value}`;
                            }
                        }
                    }
                }
            };

            const chart = new Chart(ctx, chartConfig);
            window.chartInstances.set(chartId, chart);

            // Add event listener for chart type changes
            if (chartTypeSelect) {
                chartTypeSelect.addEventListener('change', function() {
                    const chart = window.chartInstances.get(chartId);
                    if (chart) {
                        const newType = this.value;
                        const currentData = chart.data;
                        
                        // Update dataset styling based on new chart type
                        currentData.datasets = currentData.datasets.map(dataset => ({
                            ...dataset,
                            backgroundColor: dataset.backgroundColor,
                            fill: newType === 'bar',
                            borderColor: newType === 'line' ? dataset.backgroundColor : undefined,
                            borderWidth: newType === 'line' ? 2 : 1
                        }));
                        
                        chart.destroy();
                        chartConfig.type = newType;
                        chartConfig.data = currentData;
                        
                        // Update scales visibility based on chart type
                        chartConfig.options.scales.xAxes[0].display = ['bar', 'line'].includes(newType);
                        chartConfig.options.scales.yAxes[0].display = ['bar', 'line'].includes(newType);
                        
                        const newChart = new Chart(ctx, chartConfig);
                        window.chartInstances.set(chartId, newChart);
                    }
                });
            }

            // Add event listener for time period changes
            if (timePeriodSelect) {
                timePeriodSelect.addEventListener('change', function() {
                    const chart = window.chartInstances.get(chartId);
                    if (chart && originalData) {
                        const months = parseInt(this.value);
                        const newData = {
                            labels: originalData.labels.slice(-months),
                            datasets: originalData.datasets.map(dataset => ({
                                ...dataset,
                                data: dataset.data.slice(-months)
                            }))
                        };
                        chart.data = newData;
                        chart.update();
                    }
                });
            }

            // Hide loading indicator and show chart
            const loadingIndicator = container.querySelector('.loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            canvas.style.display = 'block';

        } catch (error) {
            console.error('Error initializing chart:', error);
            const errorMessage = container.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.style.display = 'block';
                errorMessage.textContent = 'Ошибка при инициализации графика: ' + error.message;
            }
            const loadingIndicator = container.querySelector('.loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        }
    }

    // Настройка Intersection Observer для ленивой загрузки графиков
    const observerOptions = {
        root: null,
        rootMargin: '50px',
        threshold: 0.1
    };

    const chartObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const container = entry.target;
                if (container.hasAttribute('data-chart-data') || container.hasAttribute('data-url')) {
                    initializeChart(container);
                }
                chartObserver.unobserve(container);
            }
        });
    }, observerOptions);

    // Наблюдаем за всеми контейнерами графиков
    document.querySelectorAll('.chart-container').forEach(container => {
        chartObserver.observe(container);
    });

    // Обработчик для кнопок показа/скрытия графиков
    document.querySelectorAll('[id^="toggleChartBtn"]').forEach(button => {
        const chartId = button.id.replace('toggleChartBtn', '');
        const chartContainer = document.getElementById(`chartContainer${chartId}`);
        
        if (button && chartContainer) {
            button.addEventListener('click', async function() {
                const isVisible = chartContainer.style.display !== 'none';
                chartContainer.style.display = isVisible ? 'none' : 'block';
                button.textContent = isVisible ? 'Показать график' : 'Скрыть график';
                button.classList.toggle('active');
                
                if (!isVisible) {
                    // Initialize chart if it doesn't exist
                    if (!window.chartInstances.has(`chartContainer${chartId}`)) {
                        const loadingIndicator = chartContainer.querySelector('.loading-indicator');
                        if (loadingIndicator) {
                            loadingIndicator.style.display = 'block';
                        }
                        
                        try {
                            await initializeChart(chartContainer);
                        } catch (error) {
                            console.error('Error initializing chart:', error);
                            if (loadingIndicator) {
                                loadingIndicator.style.display = 'none';
                            }
                            
                            // Показать сообщение об ошибке
                            const errorMessage = chartContainer.querySelector('.error-message') || document.createElement('div');
                            if (!chartContainer.querySelector('.error-message')) {
                                errorMessage.className = 'error-message';
                                chartContainer.appendChild(errorMessage);
                            }
                            errorMessage.style.display = 'block';
                            errorMessage.textContent = 'Ошибка при загрузке графика: ' + error.message;
                        }
                    }
                }
            });
        }
    });
})