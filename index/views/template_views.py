from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from index.models import Choices, Questions, Form
import random
import string
from django.http import JsonResponse
from django.shortcuts import render

def home_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not (request.user.is_superuser or request.user.is_staff):
        return HttpResponseRedirect(reverse("403"))
        
    active_forms = Form.objects.filter(is_active=True).order_by('-createdAt')
    return render(request, "index/home.html", {
        "active_forms": active_forms
    })

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
        
    # Для админов и staff показываем текущий интерфейс
    if request.user.is_superuser or request.user.is_staff:
        forms = Form.objects.all()
        return render(request, "index/index.html", {
            "forms": forms
        })
    
    # Для обычных пользователей показываем активные формы
    active_forms = Form.objects.filter(is_active=True).order_by('-createdAt')
    
    return render(request, "index/home.html", {
        "active_forms": active_forms
    })


def contact_form_template(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        name1 = Choices(choice="Вариант 1")
        name1.save()
        name = Questions(question_type = "short", question= "ФИО", required= True)
        name.save()
        name.choices.add(name1)
        name.save()
        email1 = Choices(choice="Вариант 2")
        email1.save()
        email = Questions(question_type="short", question = "Электронная почта", required = True)
        email.save()
        email.choices.add(email1)
        email.save()
        address1 = Choices(choice="Вариант 2")
        address1.save()
        address = Questions(question_type="paragraph", question="Адрес", required = True)
        address.save()
        address.choices.add(address1)
        address.save()
        phone1 = Choices(choice="Вариант 2")
        phone1.save()
        phone = Questions(question_type="short", question="Номер телефона", required = False)
        phone.save()
        phone.choices.add(phone1)
        phone.save()
        comments1 = Choices(choice="Вариант 2")
        comments1.save()
        comments = Questions(question_type = "paragraph", question = "Комментарии", required = False)
        comments.save()
        comments.choices.add(comments1)
        comments.save()
        form = Form(code = code, title = "Контактная информация", creator=request.user, background_color="#e2eee0", allow_view_score = False, edit_after_submit = True)
        form.save()
        form.questions.add(name)
        form.questions.add(email)
        form.questions.add(address)
        form.questions.add(phone)
        form.questions.add(comments)
        form.save()
        return JsonResponse({"message": "Успешно", "code": code})

def customer_feedback_template(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        comment = Choices(choice = "Комментарии")
        comment.save()
        question = Choices(choice = "Вопросы")
        question.save()
        bug = Choices(choice = "Баг-репорт")
        bug.save()
        feature = Choices(choice = "Запрос функции")
        feature.save()
        feedback_type = Questions(question = "Тип отзыва", question_type="multiple choice", required=False)
        feedback_type.save()
        feedback_type.choices.add(comment)
        feedback_type.choices.add(bug)
        feedback_type.choices.add(question)
        feedback_type.choices.add(feature)
        feedback_type.save()
        feedback1 = Choices(choice="Вариант 1")
        feedback1.save()
        feedback = Questions(question = "Отзыв", question_type="paragraph", required=True)
        feedback.save()
        feedback.choices.add(feedback1)
        feedback.save()
        suggestion1 = Choices(choice="Вариант 1")
        suggestion1.save()
        suggestion = Questions(question = "Предложения для улучшения", question_type="paragraph", required=False)
        suggestion.save()
        suggestion.choices.add(suggestion1)
        suggestion.save()
        name1 = Choices(choice="Вариант 1")
        name1.save()
        name = Questions(question = "ФИО", question_type="short", required=False)
        name.save()
        name.choices.add(name1)
        name.save()
        email1 = Choices(choice="Вариант 2")
        email1.save()
        email = Questions(question= "E-mail", question_type="short", required=False)
        email.save()
        email.choices.add(email1)
        email.save()
        form = Form(code = code, title = "Форма обратной связи", creator=request.user, background_color="#e2eee0", confirmation_message="Thanks so much for giving us feedback!",
        description = "Мы будем рады услышать ваши мысли или отзывы о том, как мы можем улучшить ваш опыт!", allow_view_score = False, edit_after_submit = True)
        form.save()
        form.questions.add(feedback_type)
        form.questions.add(feedback)
        form.questions.add(suggestion)
        form.questions.add(name)
        form.questions.add(email)
        return JsonResponse({"message": "Успешно", "code": code})

def event_registration_template(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        name1 = Choices(choice="Вариант 1")
        name1.save()
        name = Questions(question="ФИО", question_type= "short", required=True)
        name.save()
        name.choices.add(name1)
        name.save()
        email1 = Choices(choice="Вариант 2")
        email1.save()
        email = Questions(question = "E-mail", question_type="short", required=True)
        email.save()
        email.choices.add(email1)
        email.save()
        organization1 = Choices(choice="Вариант 3")
        organization1.save()
        organization = Questions(question = "Организация", question_type= "short", required=True)
        organization.save()
        organization.choices.add(organization1)
        organization.save()
        day1 = Choices(choice="Дня 1")
        day1.save()
        day2 = Choices(choice= "Дня 2")
        day2.save()
        day3 = Choices(choice= "Дня 3")
        day3.save()
        day = Questions(question="В какие дни вы будете присутствовать?", question_type="checkbox", required=True)
        day.save()
        day.choices.add(day1)
        day.choices.add(day2)
        day.choices.add(day3)
        day.save()
        dietary_none = Choices(choice="Нет")
        dietary_none.save()
        dietary_vegetarian = Choices(choice="Вегетарианское")
        dietary_vegetarian.save()
        dietary_kosher = Choices(choice="Кошерные")
        dietary_kosher.save()
        dietary_gluten = Choices(choice = "Без глютена")
        dietary_gluten.save()
        dietary = Questions(question = "Ограничения в питании", question_type="multiple choice", required = True)
        dietary.save()
        dietary.choices.add(dietary_none)
        dietary.choices.add(dietary_vegetarian)
        dietary.choices.add(dietary_gluten)
        dietary.choices.add(dietary_kosher)
        dietary.save()
        accept_agreement = Choices(choice = "Да")
        accept_agreement.save()
        agreement = Questions(question = "Я понимаю, что мне придется заплатить [ДЕНЬГИ] по прибытии", question_type="checkbox", required=True)
        agreement.save()
        agreement.choices.add(accept_agreement)
        agreement.save()
        form = Form(code = code, title = "Регистрация на мероприятие", creator=request.user, background_color="#fdefc3",
        confirmation_message="Мы приняли вашу регистрацию.\n\
Укажите здесь другую информацию.\n\
\n\
Сохраните ссылку ниже, по которой можно редактировать свою регистрацию вплоть до даты ее закрытия.",
        description = "Дата проведения: 4-6 января 2023 г.\n\
Адрес мероприятия: 123 'Ваша улица', 'Ваш город', Проспект 12345\n\
Свяжитесь с нами по телефону (123)-456-7890 и/или example@example.com", edit_after_submit=True, allow_view_score=False)
        form.save()
        form.questions.add(name)
        form.questions.add(email)
        form.questions.add(organization)
        form.questions.add(day)
        form.questions.add(dietary)
        form.questions.add(agreement)
        form.save()
        return JsonResponse({"message": "Успешно", "code": code})

def social_survey_template(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))

    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))

        def create_question(question_text, question_type, max_value=None, choices=None, is_list=False, is_negative=False):
            question = Questions(
                question=question_text,
                question_type=question_type,
                required=True,
                max_value=max_value if max_value is not None else None,
                is_list=is_list,
                is_negative=is_negative
            )
            question.save()
            if choices:
                for choice_text in choices:
                    choice = Choices(choice=choice_text)
                    choice.save()
                    question.choices.add(choice)
            question.save()
            return question

        questions = [
            ("Оценка качества работы регистратора", "range slider", 39),
            ("Визит в процедурный кабинет", "range slider", 24),
            ("Визит к врачу", "range slider", 40),
            ("Звонок в колл-центр", "range slider", 31),
            ("Звонок в МЦ", "range slider", 30),
            ("Состояние МЦ", "range slider", 30),
            ("Запрос в чате", "range slider", 20),
            ("Прикреплены ли вы к Медцентру который оцениваете?", "multiple choice", None, ["Да", "Нет"]),
            ("Способ оплаты медицинских услуг", "multiple choice", None, ["Оплачиваю услуги самостоятельно", "Покрываю свои затраты через медицинскую страховку"]),
            ("Оценка удовлетворенности", "range slider", 100),
            ("Жалобы по качеству обслуживания", "paragraph"),
            ("Предложения по улучшению качества обслуживания", "paragraph")
        ]

        created_questions = [create_question(*q) for q in questions]

        form = Form(
            code=code,
            title="Оценка медцентра",
            creator=request.user,
            background_color="#e2eee0",
            allow_view_score=False,
            edit_after_submit=True
        )
        form.save()

        for question in created_questions:
            form.questions.add(question)
        form.save()

        return JsonResponse({"message": "Успешно", "code": code})
    
# def contact_us(request):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("login"))
#     return render(request, 'index/contactUs.html')