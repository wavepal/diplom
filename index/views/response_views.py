from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from index.models import RegionMedCenter, Choices, Answer, Form, Responses, UserCity, MedCenterGroup
import json
import csv
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from openpyxl import Workbook
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
from index.templatetags.calculate_score import calculate_score
from index.templatetags.calculate_score import calculate_total_score
from django.db.models import Prefetch, Count, Avg, Q
from dateutil.relativedelta import relativedelta

@csrf_exempt
def delete_selected_responses(request):
    if request.method == "POST":
        data = json.loads(request.body)
        response_ids = data.get("response_ids", [])

        if response_ids:
            Responses.objects.filter(id__in=response_ids).delete()
            return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

def calculate_average_scores(responses, form):
    average_scores = {}
    
    # Группируем ответы по медцентрам
    for response in responses:
        med_center = response.responder_med
        if med_center not in average_scores:
            average_scores[med_center] = {
                'scores': {},
                'counts': {},
                'total_score': 0
            }
        
        # Обрабатываем каждый ответ
        for answer in response.response.filter(is_skipped=False):
            question = answer.answer_to
            if question.question_type == "range slider":
                if question.id not in average_scores[med_center]['scores']:
                    average_scores[med_center]['scores'][question.id] = 0
                    average_scores[med_center]['counts'][question.id] = 0
                
                try:
                    value = float(answer.answer)
                    # Просто суммируем исходные значения
                    average_scores[med_center]['scores'][question.id] += value
                    average_scores[med_center]['counts'][question.id] += 1
                except (ValueError, TypeError):
                    continue

    # Вычисляем средние значения
    for med_center in average_scores:
        total_valid_questions = 0
        total_percentage = 0
        
        for question_id in average_scores[med_center]['scores']:
            count = average_scores[med_center]['counts'][question_id]
            if count > 0:
                # Вычисляем среднее значение и процент от максимального
                question = form.questions.get(id=question_id)
                raw_average = average_scores[med_center]['scores'][question_id] / count
                average_scores[med_center]['scores'][question_id] = raw_average
                if question.max_value != 0:
                    percentage = (raw_average / question.max_value) * 100
                else:
                    percentage = 0
                total_percentage += percentage
                total_valid_questions += 1
        
        # Вычисляем общий средний процент
        if total_valid_questions > 0:
            average_scores[med_center]['total_score'] = round(total_percentage / total_valid_questions, 2)
        else:
            average_scores[med_center]['total_score'] = None

    return average_scores

def responses(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if not (request.user.is_admin() or request.user.is_trainer() or request.user.is_manager()):
        return HttpResponseRedirect(reverse("403"))

    formInfo = get_object_or_404(Form.objects.prefetch_related(
        'questions',
        'questions__choices'
    ), code=code)

    # Получаем параметры фильтрации
    selected_city = request.GET.get('cities')
    selected_gender = request.GET.get('gender')
    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    selected_med_region = request.GET.get('med_region')
    selected_med_center = request.GET.get('med_center')
    selected_med_group = request.GET.get('med_group')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Оптимизированный базовый запрос с prefetch_related
    all_responses = Responses.objects.filter(response_to=formInfo).select_related(
        'responder'
    ).prefetch_related(
        Prefetch('response', 
                 queryset=Answer.objects.select_related('answer_to').prefetch_related('answer_to__choices')),
    )
    
    # Применяем фильтры с использованием Q objects для оптимизации
    filters = Q()
    if selected_city:
        filters &= Q(responder_city=selected_city)
    if selected_gender:
        filters &= Q(responder_gender=selected_gender)
    if age_min:
        filters &= Q(responder_age__gte=int(age_min))
    if age_max:
        filters &= Q(responder_age__lte=int(age_max))
    if selected_med_group:
        med_centers = RegionMedCenter.objects.filter(group_id=selected_med_group).values_list('med_center', flat=True)
        filters &= Q(responder_med__in=med_centers)
    if selected_med_region:
        med_centers = RegionMedCenter.objects.filter(region=selected_med_region).values_list('med_center', flat=True)
        filters &= Q(responder_med__in=med_centers)
    if selected_med_center:
        filters &= Q(responder_med=selected_med_center)
    if date_from:
        filters &= Q(createdAt__gte=date_from)
    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
        filters &= Q(createdAt__lt=date_to)

    all_responses = all_responses.filter(filters)

    # Оптимизированная обработка данных
    responsesSummary = []
    choiceAnswered = {}
    choices_dict = {}
    
    # Предварительно загружаем все вопросы и варианты ответов
    questions = formInfo.questions.prefetch_related('choices').exclude(question_type="title")
    
    for question in questions:
        answers = Answer.objects.filter(
            answer_to=question.id, 
            is_skipped=False,
            response__in=all_responses
        ).select_related('answer_to').prefetch_related('answer_to__choices')
        
        if question.question_type in ["multiple choice", "checkbox"]:
            choiceAnswered[question.id] = {}
            for answer in answers:
                try:
                    choice = answer.answer_to.choices.get(id=answer.answer)
                    choices_dict[answer.answer] = choice.choice
                    unique_choice_key = f"{choice.choice}"
                    choiceAnswered[question.id][unique_choice_key] = choiceAnswered[question.id].get(unique_choice_key, 0) + 1
                except Choices.DoesNotExist:
                    continue

        responsesSummary.append({"question": question, "answers": answers})

    # Оптимизированный расчет средних оценок
    average_scores = calculate_average_scores(all_responses, formInfo)
    average_scores_sorted = sorted(
        [item for item in average_scores.items() if item[1]['total_score'] is not None],
        key=lambda x: x[1]['total_score'],
        reverse=True
    )

    # Оптимизированный расчет статистики медцентров
    med_center_stats = get_med_center_stats(formInfo, all_responses)

    processed_data = {
        'responsesSummary': responsesSummary,
        'choiceAnswered': choiceAnswered,
        'choices_dict': choices_dict,
        'average_scores': average_scores,
        'average_scores_sorted': average_scores_sorted,
        'med_center_stats': med_center_stats
    }
    
    # Оптимизируем получение range_slider_data
    range_slider_data = get_range_slider_data(formInfo, all_responses)
    
    # Оптимизируем получение response_answers
    response_answers = get_response_answers(all_responses, formInfo)
    
    # Оптимизируем получение user_city_dict
    user_city_dict = {response.id: response.responder_city for response in all_responses}
    
    # Оптимизируем получение average_data
    average_data = get_average_data(formInfo, all_responses)
    
    # Оптимизируем получение final_scores
    final_scores = calculate_final_scores(request, code)

    context = {
        "form": formInfo,
        "responses": all_responses,
        "responsesSummary": processed_data['responsesSummary'],
        "filteredResponsesSummary": processed_data['choiceAnswered'],
        "choices_dict": processed_data['choices_dict'],
        "average_scores_sorted": processed_data['average_scores_sorted'],
        "response_answers": response_answers,
        "city_choices": UserCity.CITY_CHOICES,
        "user_city_dict": user_city_dict,
        "range_slider_data": range_slider_data,
        "average_data": average_data,
        'med_centers': RegionMedCenter.objects.values_list('med_center', flat=True).distinct(),
        'med_center_groups': MedCenterGroup.objects.all().order_by('name'),
        "average_scores": processed_data['average_scores'],
        "med_center_stats": processed_data['med_center_stats'],
        "final_scores": final_scores,
        'active_forms': Form.objects.filter(is_active=True),
    }

    return render(request, "index/responses.html", context)

def get_filtered_responses(formInfo, age_min, age_max, selected_gender, selected_cities):
    all_responses = Responses.objects.filter(response_to=formInfo)
    
    # Используем сохраненные статические данные вместо связей
    if age_min:
        all_responses = all_responses.filter(responder_age__gte=int(age_min))
    if age_max:
        all_responses = all_responses.filter(responder_age__lte=int(age_max))
    if selected_gender:
        all_responses = all_responses.filter(responder_gender=selected_gender)
    if selected_cities and selected_cities != ['']:
        all_responses = all_responses.filter(responder_city__in=selected_cities)
    
    return all_responses

def process_questions_and_answers(formInfo):
    responsesSummary = []
    choiceAnswered = {}
    choices_dict = {}

    for question in formInfo.questions.exclude(question_type="title"):
        answers = Answer.objects.filter(answer_to=question.id, is_skipped=False)

        if question.question_type in ["multiple choice", "checkbox"]:
            choiceAnswered[question.id] = choiceAnswered.get(question.id, {})
            for answer in answers:
                try:
                    choice = answer.answer_to.choices.get(id=answer.answer)
                    choices_dict[answer.answer] = choice.choice
                    unique_choice_key = f"{choice.choice}"
                    choiceAnswered[question.id][unique_choice_key] = choiceAnswered[question.id].get(unique_choice_key, 0) + 1
                except Choices.DoesNotExist:
                    continue

        responsesSummary.append({"question": question, "answers": answers})
    
    return responsesSummary, choiceAnswered, choices_dict

def get_range_slider_data(formInfo, all_responses):
    data = {}
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    current_month = end_date.replace(day=1)
    months = [(current_month - relativedelta(months=i)).strftime('%B %Y') for i in range(12)]
    months.reverse()

    questions = formInfo.questions.filter(question_type="range slider").exclude(question_type="title")
    
    for question in questions:
        try:
            responses_for_question = Answer.objects.filter(
                answer_to=question,
                response__in=all_responses,
                response__createdAt__gte=start_date,
                is_skipped=False
            ).select_related('response')
            
            # Get unique centers first
            centers = responses_for_question.values_list('response__responder_med', flat=True).distinct()
            monthly_averages_by_center = {center: [0] * 12 for center in centers if center is not None}

            # Calculate monthly averages using raw SQL to avoid OperationalError
            monthly_data = Answer.objects.filter(
                answer_to=question,
                response__in=all_responses,
                response__createdAt__gte=start_date,
                is_skipped=False
            ).extra(
                select={'month': "strftime('%%m', createdAt)"}
            ).values(
                'response__responder_med',
                'month'
            ).annotate(
                avg_value=Avg('answer')
            )

            for item in monthly_data:
                center = item['response__responder_med']
                if center is not None and center in monthly_averages_by_center:
                    try:
                        month = int(item['month'])
                        month_idx = (end_date.month - month) % 12
                        if 0 <= month_idx < 12:
                            avg_value = item['avg_value']
                            if avg_value is not None:
                                monthly_averages_by_center[center][11 - month_idx] = round(float(avg_value), 2)
                    except (ValueError, TypeError, IndexError) as e:
                        continue

            data[question.id] = {
                'months': months,
                'averages_by_center': monthly_averages_by_center,
                'max_value': question.max_value
            }
        except Exception as e:
            continue
    
    return data

def get_response_answers(all_responses, formInfo):
    data = {}
    questions = formInfo.questions.prefetch_related('choices').exclude(question_type="title")
    
    for response in all_responses:
        data[response.id] = {}
        answers = response.response.select_related('answer_to').prefetch_related('answer_to__choices')
        
        for answer in answers:
            question = answer.answer_to
            if not answer.is_skipped:
                if question.question_type == "checkbox":
                    selected_choices = []
                    choice_ids = answer.answer.split(',') if answer.answer else []
                    choices = question.choices.filter(id__in=choice_ids)
                    selected_choices = [choice.choice for choice in choices]
                    data[response.id][question.id] = selected_choices if selected_choices else "N/A"
                elif question.question_type == "multiple choice":
                    try:
                        choice = question.choices.get(id=answer.answer)
                        data[response.id][question.id] = choice.choice
                    except Choices.DoesNotExist:
                        data[response.id][question.id] = "N/A"
                else:
                    data[response.id][question.id] = answer.answer
            else:
                data[response.id][question.id] = "N/A"
                    
    return data

def get_filtered_response_summary(choiceAnswered, all_responses, formInfo):
    # Создаем словарь для хранения результатов
    filteredResponsesSummary = {}
    
    # Инициализируем счетчики для каждого вопроса и варианта ответа
    for question in formInfo.questions.exclude(question_type="title"):
        if question.question_type in ["multiple choice", "checkbox"]:
            filteredResponsesSummary[question.id] = {}
            for choice in question.choices.all():
                filteredResponsesSummary[question.id][choice.choice] = 0

    # Подсчитываем ответы для отфильтрованных респондентов
    for response in all_responses:
        for question in formInfo.questions.exclude(question_type="title"):
            if question.question_type in ["multiple choice", "checkbox"]:
                answers = Answer.objects.filter(
                    response=response, 
                    answer_to=question.id, 
                    is_skipped=False
                )
                
                if question.question_type == "checkbox":
                    for answer in answers:
                        try:
                            choice = question.choices.get(id=answer.answer)
                            filteredResponsesSummary[question.id][choice.choice] += 1
                        except Choices.DoesNotExist:
                            continue
                else:  # multiple choice
                    answer = answers.first()
                    if answer:
                        try:
                            choice = question.choices.get(id=answer.answer)
                            filteredResponsesSummary[question.id][choice.choice] += 1
                        except Choices.DoesNotExist:
                            continue

    return filteredResponsesSummary

def get_user_city_dict(all_responses):
    # Больше не нужно делать дополнительные запросы к UserCity
    user_city_dict = {}
    for response in all_responses:
        user_city_dict[response.id] = response.responder_city
    return user_city_dict

def get_average_data(formInfo, all_responses):
    average_data = {}
    questions = formInfo.questions.prefetch_related('choices').exclude(question_type="title")

    for question in questions:
        if question.question_type == "range slider":
            question_average_data = {}
            responders = all_responses.values_list('responder_med', flat=True).distinct()

            for responder_med in responders:
                selected_responses = all_responses.filter(responder_med=responder_med)
                range_answers = Answer.objects.filter(
                    response__in=selected_responses,
                    answer_to=question.id,
                    is_skipped=False
                )

                if range_answers.exists():
                    average_value = range_answers.aggregate(Avg('answer'))['answer__avg']
                    question_average_data[responder_med] = average_value if average_value is not None else 0
                else:
                    question_average_data[responder_med] = 0

            average_data[question.id] = question_average_data
    
    return average_data

def get_med_center_stats(formInfo, all_responses):
    med_center_stats = {}
    med_centers = RegionMedCenter.objects.all()

    # Инициализируем статистику используя ID медцентра
    for med_center in med_centers:
        med_center_stats[med_center.med_center] = {
            'total_responses': 0,
            'questions': {},
        }
        for question in formInfo.questions.filter(is_negative=True):
            med_center_stats[med_center.med_center]['questions'][question.id] = 0

    # Подсчитываем статистику
    for response in all_responses:
        med_center = response.responder_med
        if med_center in med_center_stats:
            med_center_stats[med_center]['total_responses'] += 1
            
            # Используем response вместо answers
            for answer in response.response.all():
                if answer.answer_to.is_negative and answer.answer == 'Да':
                    med_center_stats[med_center]['questions'][answer.answer_to.id] += 1

    return med_center_stats


def export_responses_to_excel(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    formInfo = get_object_or_404(Form, code=code)

    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseRedirect(reverse("403"))

    # Получаем состояния чекбоксов
    export_as_percentage = request.GET.get('export_as_percentage') == 'true'
    export_total_as_percentage = request.GET.get('export_total_as_percentage') == 'true'
    hidden_columns = request.GET.get('hidden_columns', '').split(',')

    # Получаем параметры фильтрации из сессии
    filter_params = request.session.get('filter_params', {})
    
    # Получаем параметры фильтрации из сессии или из GET-параметров
    selected_city = request.GET.get('cities', filter_params.get('cities'))
    selected_gender = request.GET.get('gender', filter_params.get('gender'))
    age_min = request.GET.get('age_min', filter_params.get('age_min'))
    age_max = request.GET.get('age_max', filter_params.get('age_max'))
    selected_med_region = request.GET.get('med_region', filter_params.get('med_region'))
    selected_med_center = request.GET.get('med_center', filter_params.get('med_center'))
    selected_med_group = request.GET.get('med_group', filter_params.get('med_group'))
    date_from = request.GET.get('date_from', filter_params.get('date_from'))
    date_to = request.GET.get('date_to', filter_params.get('date_to'))
    
    # Базовый запрос
    all_responses = Responses.objects.filter(response_to=formInfo)
    
    # Применяем фильтры
    if selected_city:
        all_responses = all_responses.filter(responder_city=selected_city)
    
    if selected_gender:
        all_responses = all_responses.filter(responder_gender=selected_gender)
    
    if age_min:
        all_responses = all_responses.filter(responder_age__gte=int(age_min))
    
    if age_max:
        all_responses = all_responses.filter(responder_age__lte=int(age_max))

    # Фильтрация по группе медцентров
    if selected_med_group:
        med_centers = RegionMedCenter.objects.filter(group_id=selected_med_group).values_list('med_center', flat=True)
        all_responses = all_responses.filter(responder_med__in=med_centers)

    # Фильтрация по региону медцентра
    if selected_med_region:
        med_centers = RegionMedCenter.objects.filter(region=selected_med_region).values_list('med_center', flat=True)
        all_responses = all_responses.filter(responder_med__in=med_centers)

    # Фильтрация по конкретному медцентру
    if selected_med_center:
        all_responses = all_responses.filter(responder_med=selected_med_center)

    # Фильтрация по датам
    if date_from:
        all_responses = all_responses.filter(createdAt__gte=date_from)
    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
        all_responses = all_responses.filter(createdAt__lt=date_to)

    # Применяем фильтры по выбранным вариантам ответов
    for question_id, selected_choices in filter_params.get('choices', {}).items():
        answers = Answer.objects.filter(
            response__in=all_responses,
            answer_to_id=question_id,
            answer__in=selected_choices
        )
        response_ids = answers.values_list('response_id', flat=True)
        all_responses = all_responses.filter(id__in=response_ids)

    response_answers = {}
    for response in all_responses:
        response_answers[response.id] = {}
        for question in formInfo.questions.exclude(question_type="title"):
            if question.question_type == "checkbox":
                answers = Answer.objects.filter(response=response, answer_to=question.id, is_skipped=False)
                selected_choices = []
                for answer in answers:
                    try:
                        choice = answer.answer_to.choices.get(id=answer.answer)
                        selected_choices.append(choice.choice)
                    except Choices.DoesNotExist:
                        continue
                response_answers[response.id][question.id] = selected_choices if selected_choices else "N/A"
            else:
                answer = Answer.objects.filter(response=response, answer_to=question.id, is_skipped=False).first()
                if answer:
                    if question.question_type == "multiple choice":
                        try:
                            choice = question.choices.get(id=answer.answer)
                            response_answers[response.id][question.id] = choice.choice
                        except Choices.DoesNotExist:
                            response_answers[response.id][question.id] = "N/A"
                    elif question.question_type == "range slider":
                        try:
                            raw_value = float(answer.answer)
                        except ValueError:
                            raw_value = 0.0
                        max_range_value = question.max_value
                        if export_as_percentage:
                            percentage = (raw_value / max_range_value) * 100 if max_range_value != 0 else 0
                            response_answers[response.id][question.id] = f"{percentage:.2f}%"
                        else:
                            response_answers[response.id][question.id] = raw_value
                    elif question.question_type in ["short", "paragraph"]:
                        response_answers[response.id][question.id] = answer.answer if answer.answer.strip() else "N/A"
                    else:
                        response_answers[response.id][question.id] = answer.answer
                else:
                    response_answers[response.id][question.id] = "N/A"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Responses"

    headers = ["User", "Age", "Gender", "City", "Medical Center", "Submission Date"]
    question_headers = {question.question: question.id for question in formInfo.questions.exclude(question_type="title")}

    headers = [header for header in headers if header.lower() not in hidden_columns]
    for question, question_id in question_headers.items():
        if f"question-{question_id}" not in hidden_columns:
            headers.append(question)
    if "total-score" not in hidden_columns and formInfo.is_quiz:
        headers.append("Total Score (Percentage)" if export_total_as_percentage else "Total Score")

    # Стили для заголовков
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

    # Записываем заголовки и применяем стили
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')

    for row_num, response in enumerate(all_responses, 2):
        row = []
        responder = response.responder
        row_data = {
            "User": response.responder_username if response.responder else "Anonymous",
            "Age": response.responder_age if response.responder_age else "N/A",
            "Gender": response.responder_gender if response.responder_gender else "N/A",
            "City": response.responder_city if response.responder_city else "N/A",
            "Medical Center": response.responder_med if response.responder_med else "N/A",
            "Submission Date": response.createdAt.strftime("%d.%m.%Y %H:%M")
        }

        for question, question_id in question_headers.items():
            if f"question-{question_id}" not in hidden_columns:
                answer = response_answers[response.id].get(question_id, "N/A")
                row_data[question] = answer

        if "total-score" not in hidden_columns and formInfo.is_quiz:
            total_score = calculate_score(response, formInfo)
            if export_total_as_percentage:
                total_percentage = (total_score / calculate_total_score(formInfo)) * 100
                row_data["Total Score (Percentage)"] = f"{total_percentage:.2f}%"
            else:
                row_data["Total Score"] = total_score

        row = [row_data[col] for col in headers]
        for col_num, value in enumerate(row, 1):
            ws.cell(row=row_num, column=col_num, value=value)

    # Автоматическая настройка ширины столбцов
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="responses.xlsx"'
    return response

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill

def export_combined_excel(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    formInfo = get_object_or_404(Form, code=code)

    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseRedirect(reverse("403"))

    visible_columns = request.GET.get('visible_columns', '').split(',')
    visible_med_centers = request.GET.get('visible_med_centers', '').split(',')
    export_as_percentage = request.GET.get('export_as_percentage') == 'true'
    export_total_as_percentage = request.GET.get('export_total_as_percentage') == 'true'

    # Получаем параметры фильтрации из сессии
    filter_params = request.session.get('filter_params', {})
    
    # Применяем те же фильтры, что и в представлении responses
    all_responses = Responses.objects.filter(response_to=formInfo)
    
    if filter_params.get('cities'):
        all_responses = all_responses.filter(responder__city_info__city=filter_params['cities'])
    
    if filter_params.get('gender'):
        all_responses = all_responses.filter(responder__gender_info__gender=filter_params['gender'])
    
    if filter_params.get('age_min'):
        all_responses = all_responses.filter(responder_age__gte=int(filter_params['age_min']))
    
    if filter_params.get('age_max'):
        all_responses = all_responses.filter(responder_age__lte=int(filter_params['age_max']))

    if filter_params.get('med_region'):
        med_centers = RegionMedCenter.objects.filter(
            region=filter_params['med_region']
        ).values_list('med_center', flat=True)
        all_responses = all_responses.filter(responder_med__in=med_centers)

    if filter_params.get('med_center'):
        all_responses = all_responses.filter(responder_med=filter_params['med_center'])

    # Применяем фильтры по выбранным вариантам ответов
    for question_id, selected_choices in filter_params.get('choices', {}).items():
        answers = Answer.objects.filter(
            response__in=all_responses,
            answer_to_id=question_id,
            answer__in=selected_choices
        )
        response_ids = answers.values_list('response_id', flat=True)
        all_responses = all_responses.filter(id__in=response_ids)

    average_scores = calculate_average_scores(all_responses, formInfo)
    average_scores_sorted = sorted(
        [item for item in average_scores.items() if item[1]['total_score'] is not None],
        key=lambda x: x[1]['total_score'],
        reverse=True
    )
    med_center_stats = get_med_center_stats(formInfo, all_responses)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Combined Data"

    # Стили для заголовков
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    
    # Заголовки для средних оценок
    headers = ["Медицинский центр"]
    for question in formInfo.questions.filter(question_type="range slider"):
        if f'{question.id}' in visible_columns:
            headers.append(f"{question.question}")
    
    # Добавляем заголовки для количества ответов
    for question in formInfo.questions.filter(question_type__in=["short", "paragraph"]):
        if f'answ-{question.id}' in visible_columns:
            headers.append(f"Кол-во ответов: {question.question}")
    
    if 'main-value' in visible_columns:
        headers.append("Общая оценка")
    if 'total-responses' in visible_columns:
        headers.append("Общее количество ответов")

    # Записываем заголовки и применяем стили
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(wrap_text=True)

    # Заполняем данные
    row_num = 2
    for med_center, scores in average_scores_sorted:
        if med_center not in visible_med_centers:
            continue
        
        row = [med_center]
        
        # Добавляем значения range slider
        for question in formInfo.questions.filter(question_type="range slider"):
            if f'{question.id}' in visible_columns:
                raw_value = scores['scores'].get(question.id, "N/A")
                if raw_value != "N/A" and export_as_percentage:
                    max_value = question.max_value
                    percentage = (raw_value / max_value) * 100
                    row.append(f"{percentage:.2f}%")
                else:
                    row.append(raw_value)
        
        # Добавляем количество ответов для каждого вопроса
        for question in formInfo.questions.filter(question_type__in=["short", "paragraph"]):
            if f'answ-{question.id}' in visible_columns:
                answers_count = med_center_stats[med_center]['questions'].get(question.id, 0)
                row.append(answers_count)
        
        # Добавляем общую оценку
        if 'main-value' in visible_columns:
            total_score = scores['total_score']
            if export_total_as_percentage:
                total_score = f"{total_score:.2f}%"
            row.append(total_score)
        
        if 'total-responses' in visible_columns:
            row.append(med_center_stats[med_center]['total_responses'])
        
        for col_num, value in enumerate(row, 1):
            ws.cell(row=row_num, column=col_num, value=value)
        row_num += 1

    # Настраиваем ширину столбцов
    for col_num, column_title in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        ws.column_dimensions[column_letter].width = 20

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Combined_Data_{formInfo.code}.xlsx'
    wb.save(response)

    return response

def retrieve_checkbox_choices(response, question):
    checkbox_answers = []

    answers = Answer.objects.filter(answer_to=question, response=response, is_skipped=False)
    for answer in answers:
        selected_choice_ids = answer.answer.split(',')  
        selected_choices = Choices.objects.filter(pk__in=selected_choice_ids)
        checkbox_answers.append([choice.choice for choice in selected_choices])

    return checkbox_answers

def exportcsv(request,code):
    formInfo = Form.objects.filter(code = code)
    formInfo = formInfo[0]
    responses=Responses.objects.filter(response_to = formInfo)
    questions = formInfo.questions.all()


    http_response = HttpResponse()
    http_response['Content-Type'] = 'text/csv'
    http_response['Content-Disposition'] = f'attachment; filename={formInfo.title}.csv'
    writer = csv.writer(http_response)
    header = ['Response Code', 'Responder', 'Responder Email','Responder_ip']

    for question in questions:
        header.append(question.question)

    writer.writerow(header)

    for response in responses:
        response_data = [
        response.response_code,
        response.responder_username if response.responder else 'Anonymous',
        response.responder_email if response.responder_email else '',
        response.responder_ip if response.responder_ip else ''
    ]
        for question in questions:
            answer = Answer.objects.filter(answer_to=question, response=response, is_skipped=False).first()


            if  question.question_type not in ['multiple choice','checkbox']:
                response_data.append(answer.answer if answer else '')
            elif question.question_type == "multiple choice":
                response_data.append(answer.answer_to.choices.get(id = answer.answer).choice if answer else '')
            elif question.question_type == "checkbox":
                if answer and question.question_type == 'checkbox':
                    checkbox_choices = retrieve_checkbox_choices(response,answer.answer_to)
                    response_data.append(checkbox_choices)

        print(response_data)
        writer.writerow(response_data)

    return http_response

def response(request, code, response_code):
    formInfo = Form.objects.filter(code=code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    if not formInfo.allow_view_score:
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse("403"))

    total_score = 0
    score = 0
    responseInfo = Responses.objects.filter(response_code=response_code)
    if responseInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        responseInfo = responseInfo[0]

    if formInfo.is_quiz:
        for question in formInfo.questions.all():
            if question.question_type == "multiple choice":
                max_choice_score = max([choice.scores for choice in question.choices.all()])
                total_score += max_choice_score + question.score
            elif question.question_type == "checkbox":
                choices_total_score = sum([choice.scores for choice in question.choices.all()])
                total_score += choices_total_score + question.score
            else:
                total_score += question.score

        _temp = []
        for response in responseInfo.response.all():
            if response.answer_to.question_type in ["short", "paragraph"]:
                if response.answer == response.answer_to.answer_key:
                    score += response.answer_to.score
            elif response.answer_to.question_type == "multiple choice":
                answerKey = None
                choice_score = 0
                for choice in response.answer_to.choices.all():
                    if choice.is_answer:
                        answerKey = choice.id
                    if choice.id == int(response.answer):
                        choice_score = choice.scores
                if answerKey is not None and int(answerKey) == int(response.answer):
                    score += response.answer_to.score + choice_score
            elif response.answer_to.question_type == "checkbox" and response.answer_to.pk not in _temp:
                answers = []
                answer_keys = []
                choice_scores_sum = 0
                selected_scores_sum = 0
                for resp in responseInfo.response.filter(answer_to__pk=response.answer_to.pk):
                    answers.append(int(resp.answer))
                    for choice in resp.answer_to.choices.all():
                        if choice.is_answer and choice.pk not in answer_keys:
                            answer_keys.append(choice.pk)
                        if choice.pk == int(resp.answer):
                            selected_scores_sum += choice.scores
                    _temp.append(response.answer_to.pk)
                if set(answers) == set(answer_keys):
                    score += response.answer_to.score
                score += selected_scores_sum

    return render(request, "index/response.html", {
        "form": formInfo,
        "response": responseInfo,
        "score": score,
        "total_score": total_score
    })

def export_final_scores(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    formInfo = get_object_or_404(Form, code=code)
    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseRedirect(reverse("403"))

    # Получаем активные формы и данные
    active_forms = Form.objects.filter(is_active=True)
    final_scores = calculate_final_scores(request, code)

    # Создаем Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Итоговые оценки"

    # Создаем заголовки
    headers = ["Медицинский центр"]
    for form in active_forms:
        headers.append(form.title)
    headers.extend(["Количество жалоб", "Процент влияния жалоб", "Итоговая оценка"])

    # Применяем стили к заголовкам
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
        # Устанавливаем ширину столбца
        ws.column_dimensions[get_column_letter(col)].width = 20

    # Заполняем данные
    row = 2
    for med_center, data in final_scores.items():
        col = 1
        # Медцентр
        ws.cell(row=row, column=col, value=med_center)
        col += 1
        
        # Оценки по формам
        for form in active_forms:
            score = data['forms'].get(form.title, 'N/A')
            if score != 'N/A':
                ws.cell(row=row, column=col, value=float(score))
            else:
                ws.cell(row=row, column=col, value=score)
            col += 1
        
        # Количество жалоб
        ws.cell(row=row, column=col, value=data['negative_count'])
        col += 1
        
        # Процент влияния жалоб (делим на 100, так как значение уже в процентах)
        percentage_cell = ws.cell(row=row, column=col, value=data['negative_percentage'] / 100)
        percentage_cell.number_format = '0%'
        col += 1
        
        # Итоговая оценка
        ws.cell(row=row, column=col, value=data['total_score'])
        
        row += 1

    # Создаем HTTP ответ
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=Final_Scores_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

    # Сохраняем файл
    wb.save(response)
    return response

def edit_response(request, code, response_code):
    formInfo = Form.objects.filter(code=code).first()
    if not formInfo:
        return HttpResponseRedirect(reverse('404'))
    
    response = Responses.objects.filter(response_code=response_code, response_to=formInfo).first()
    if not response:
        return HttpResponseRedirect(reverse('404'))
    
    if formInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        if response.responder != request.user:
            return HttpResponseRedirect(reverse('403'))
    
    if request.method == "POST":
        if formInfo.authenticated_responder and not response.responder:
            response.responder = request.user
            response.save()
        if formInfo.collect_email:
            response.responder_email = request.POST["email-address"]
            response.save()
        for i in response.response.all():
            i.delete()
        for i in request.POST:
            if i == "csrfmiddlewaretoken" or i == "email-address":
                continue
            question = formInfo.questions.get(id=i)
            for j in request.POST.getlist(i):
                is_skipped = request.POST.get(f'is_skipped_{question.id}') == 'True'
                answer = Answer(answer=j, answer_to=question, is_skipped=is_skipped)
                answer.save()
                response.response.add(answer)
                response.save()
        if formInfo.is_quiz:
            return HttpResponseRedirect(reverse("response", args=[formInfo.code, response.response_code]))
        else:
            return render(request, "index/form_response.html", {
                "form": formInfo,
                "code": response.response_code
            })
    return render(request, "index/edit_response.html", {
        "form": formInfo,
        "response": response
    })

def delete_responses(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        responses = Responses.objects.filter(response_to = formInfo)
        for response in responses:
            for i in response.response.all():
                i.delete()
            response.delete()
        return JsonResponse({"message": "Успешно"})
    

def calculate_final_scores(request, code):
    final_scores = {}
    active_forms = Form.objects.filter(is_active=True)
    
    for form in active_forms:
        responses = Responses.objects.filter(response_to=form)
        average_scores = calculate_average_scores(responses, form)
        
        for med_center, data in average_scores.items():
            if med_center not in final_scores:
                final_scores[med_center] = {
                    'forms': {},
                    'total_score': 0,
                    'negative_count': 0,
                    'negative_percentage': 0
                }
            
            if data['total_score'] is not None:
                # Сохраняем процентное значение
                final_scores[med_center]['forms'][form.title] = data['total_score']
    
    # Подсчет негативных ответов и их влияния
    current_form = Form.objects.get(code=code)
    current_responses = Responses.objects.filter(response_to=current_form)
    
    for med_center in final_scores:
        negative_count = 0
        total_forms = 0
        total_percentage = 0
        
        # Подсчет негативных ответов
        med_center_responses = current_responses.filter(responder_med=med_center)
        for response in med_center_responses:
            for answer in response.response.filter(answer_to__is_negative=True, answer='Да'):
                negative_count += 1
        
        # Расчет среднего процента по всем формам
        for score in final_scores[med_center]['forms'].values():
            if score is not None:
                total_percentage += score
                total_forms += 1
        
        final_scores[med_center]['negative_count'] = negative_count
        
        # Расчет влияния негативных ответов
        if total_forms > 0:
            average_percentage = total_percentage / total_forms
            negative_impact = negative_count * 5  # 5% за каждый негативный ответ
            final_scores[med_center]['negative_percentage'] = min(negative_impact, 100)
            final_scores[med_center]['total_score'] = max(0, round(average_percentage * (1 - negative_impact / 100), 2))
        else:
            final_scores[med_center]['total_score'] = 0
            final_scores[med_center]['negative_percentage'] = 0
    
    return final_scores

@csrf_exempt
def check_question_has_answers(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    from index.models import Questions, Answer
    question = Questions.objects.filter(id=question_id).first()
    
    if not question:
        return JsonResponse({'error': 'Question not found'}, status=404)
    
    has_answers = Answer.objects.filter(answer_to=question).exists()
    
    return JsonResponse({
        'has_answers': has_answers
    })