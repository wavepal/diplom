document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#create-blank-form").addEventListener("click", () => {
        const csrf = Cookies.get('csrftoken');
        fetch('/form/create', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({
                title: "Без названия"
            })
        })
        .then(response => response.json())
        .then(result => {
            window.location = `/form/${result.code}/edit`
        })
    })
    document.querySelector("#create-contact-form").addEventListener("click", () => {
        const csrf = Cookies.get('csrftoken');
        fetch('/form/create/contact', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(result => {
            window.location = `/form/${result.code}/edit`
        })
    })
    document.querySelector("#create-customer-feedback").addEventListener("click", () => {
        const csrf = Cookies.get('csrftoken');
        fetch('/form/create/feedback', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(result => {
            window.location = `/form/${result.code}/edit`
        })
    })
    document.querySelector("#create-event-registration").addEventListener("click", () => {
        const csrf = Cookies.get('csrftoken');
        fetch('/form/create/event', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(result => {
            window.location = `/form/${result.code}/edit`
        })
    })
    document.querySelector("#create-social-survey").addEventListener("click", () => {
        const csrf = Cookies.get('csrftoken');
        fetch('/form/create/survey', {
            method: "POST",
            headers: {'X-CSRFToken': csrf},
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(result => {
            window.location = `/form/${result.code}/edit`
        })
    })
})