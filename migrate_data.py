import os
import sqlite3
import django
from datetime import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'form.settings')
django.setup()

from django.contrib.auth import get_user_model
from index.models import Form, Questions, Choices, Answer, Responses, RegionMedCenter, MedCenterGroup

User = get_user_model()

def make_aware(datetime_str):
    if not datetime_str:
        return None
    try:
        # Try with microseconds
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            # Try without microseconds
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # Try just date and time
                dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            except ValueError:
                return None
    
    if not timezone.is_aware(dt):
        return timezone.make_aware(dt)
    return dt

def migrate_data():
    # Connect to old database
    old_conn = sqlite3.connect('db.sqlite3.old')
    old_cur = old_conn.cursor()
    
    # Clear existing data
    print("Clearing existing data...")
    User.objects.all().delete()
    MedCenterGroup.objects.all().delete()
    RegionMedCenter.objects.all().delete()
    Form.objects.all().delete()
    Questions.objects.all().delete()
    Choices.objects.all().delete()
    Answer.objects.all().delete()
    Responses.objects.all().delete()
    
    # First, migrate users
    print("Migrating users...")
    old_cur.execute("""
        SELECT index_user.id, username, email, password, is_superuser, is_staff, is_active, date_joined,
               city_info.city, med_info.med_center, date_info.date_of_birth, gender_info.gender,
               desc_info.desc, role_info.role
        FROM index_user
        LEFT JOIN index_usercity city_info ON index_user.id = city_info.user_id
        LEFT JOIN index_usermed med_info ON index_user.id = med_info.user_id
        LEFT JOIN index_dateofbirth date_info ON index_user.id = date_info.user_id
        LEFT JOIN index_usergender gender_info ON index_user.id = gender_info.user_id
        LEFT JOIN index_userdesc desc_info ON index_user.id = desc_info.user_id
        LEFT JOIN index_userrole role_info ON index_user.id = role_info.user_id
    """)
    
    users = old_cur.fetchall()
    for user_data in users:
        (user_id, username, email, password, is_superuser, is_staff, is_active, date_joined,
         city, med_center, date_of_birth, gender, description, role) = user_data
        
        try:
            user = User.objects.create(
                id=user_id,
                username=username,
                email=email,
                password=password,
                is_superuser=is_superuser,
                is_staff=is_staff,
                is_active=is_active,
                date_joined=make_aware(date_joined),
                city=city,
                med_center=med_center,
                date_of_birth=date_of_birth if date_of_birth else None,
                gender=gender,
                description=description,
                role=role if role else 'USER'
            )
            print(f"Migrated user: {username}")
        except Exception as e:
            print(f"Error migrating user {username}: {str(e)}")
    
    # Migrate MedCenterGroups
    print("\nMigrating med center groups...")
    old_cur.execute("SELECT id, name, description, created_at FROM index_medcentergroup")
    for group_data in old_cur.fetchall():
        group_id, name, description, created_at = group_data
        try:
            MedCenterGroup.objects.create(
                id=group_id,
                name=name,
                description=description,
                created_at=make_aware(created_at)
            )
            print(f"Migrated med center group: {name}")
        except Exception as e:
            print(f"Error migrating med center group {name}: {str(e)}")
    
    # Migrate RegionMedCenters
    print("\nMigrating region med centers...")
    old_cur.execute("""
        SELECT id, region, med_center, address, group_id 
        FROM index_regionmedcenter
    """)
    for center_data in old_cur.fetchall():
        center_id, region, med_center, address, group_id = center_data
        try:
            RegionMedCenter.objects.create(
                id=center_id,
                region=region,
                med_center=med_center,
                address=address,
                group_id=group_id
            )
            print(f"Migrated region med center: {med_center}")
        except Exception as e:
            print(f"Error migrating region med center {med_center}: {str(e)}")
    
    # First migrate all questions and choices
    print("\nMigrating questions and choices...")
    old_cur.execute("""
        SELECT id, question, question_type, required, answer_key, score,
               feedback, max_value, is_list, is_skip, is_negative, "order"
        FROM index_questions
    """)
    for q_data in old_cur.fetchall():
        try:
            question = Questions.objects.create(
                id=q_data[0],
                question=q_data[1],
                question_type=q_data[2],
                required=q_data[3],
                answer_key=q_data[4],
                score=q_data[5],
                feedback=q_data[6],
                max_value=q_data[7],
                is_list=q_data[8],
                is_skip=q_data[9],
                is_negative=q_data[10],
                order=q_data[11]
            )
            
            # Migrate choices for this question
            old_cur.execute("""
                SELECT choice_id FROM index_questions_choices
                WHERE questions_id = ?
            """, (q_data[0],))
            for (choice_id,) in old_cur.fetchall():
                old_cur.execute("""
                    SELECT id, choice, is_answer, scores
                    FROM index_choices WHERE id = ?
                """, (choice_id,))
                c_data = old_cur.fetchone()
                if c_data:
                    choice = Choices.objects.create(
                        id=c_data[0],
                        choice=c_data[1],
                        is_answer=c_data[2],
                        scores=c_data[3]
                    )
                    question.choices.add(choice)
            print(f"Migrated question: {q_data[1][:50]}...")
        except Exception as e:
            print(f"Error migrating question {q_data[1][:50]}: {str(e)}")
    
    # Migrate Forms
    print("\nMigrating forms...")
    old_cur.execute("""
        SELECT id, code, title, description, creator_id, background_color, text_color,
               collect_email, authenticated_responder, edit_after_submit, confirmation_message,
               createdAt, is_single_form, is_active, updatedAt
        FROM index_form
    """)
    for form_data in old_cur.fetchall():
        (form_id, code, title, description, creator_id, bg_color, text_color,
         collect_email, auth_responder, edit_after_submit, confirmation_msg,
         created_at, is_single_form, is_active, updated_at) = form_data
        
        try:
            form = Form.objects.create(
                id=form_id,
                code=code,
                title=title,
                description=description,
                creator_id=creator_id,
                background_color=bg_color,
                text_color=text_color,
                collect_email=collect_email,
                authenticated_responder=auth_responder,
                edit_after_submit=edit_after_submit,
                confirmation_message=confirmation_msg,
                createdAt=make_aware(created_at),
                is_single_form=is_single_form,
                is_active=is_active,
                allow_med_center_choice=False,  # Default value for new field
                updatedAt=make_aware(updated_at)
            )
            print(f"Migrated form: {title}")
            
            # Add questions to form
            old_cur.execute("""
                SELECT questions_id FROM index_form_questions
                WHERE form_id = ?
            """, (form_id,))
            for (question_id,) in old_cur.fetchall():
                question = Questions.objects.filter(id=question_id).first()
                if question:
                    form.questions.add(question)
        except Exception as e:
            print(f"Error migrating form {title}: {str(e)}")
    
    # Migrate Responses
    print("\nMigrating responses...")
    old_cur.execute("""
        SELECT id, response_code, response_to_id, responder_ip, responder_id,
               responder_email, authenticated_responder, responder_gender,
               responder_birth_date, responder_age, responder_city,
               responder_med, responder_username, createdAt
        FROM index_responses
    """)
    for response_data in old_cur.fetchall():
        (response_id, response_code, form_id, responder_ip, responder_id,
         responder_email, auth_responder, responder_gender, responder_birth_date,
         responder_age, responder_city, responder_med, responder_username,
         created_at) = response_data
        
        try:
            response = Responses.objects.create(
                id=response_id,
                response_code=response_code,
                response_to_id=form_id,
                responder_ip=responder_ip,
                responder_id=responder_id,
                responder_email=responder_email,
                authenticated_responder=auth_responder,
                responder_gender=responder_gender,
                responder_birth_date=responder_birth_date,
                responder_age=responder_age,
                responder_city=responder_city,
                responder_med=responder_med,
                responder_username=responder_username,
                createdAt=make_aware(created_at)
            )
            
            # Migrate answers for this response
            old_cur.execute("""
                SELECT answer_id FROM index_responses_response
                WHERE responses_id = ?
            """, (response_id,))
            for (answer_id,) in old_cur.fetchall():
                old_cur.execute("""
                    SELECT id, answer, answer_to_id, is_skipped
                    FROM index_answer WHERE id = ?
                """, (answer_id,))
                a_data = old_cur.fetchone()
                if a_data:
                    answer = Answer.objects.create(
                        id=a_data[0],
                        answer=a_data[1],
                        answer_to_id=a_data[2],
                        is_skipped=a_data[3]
                    )
                    response.response.add(answer)
            
            print(f"Migrated response: {response_code}")
        except Exception as e:
            print(f"Error migrating response {response_code}: {str(e)}")
    
    old_conn.close()
    print("\nMigration completed!")

if __name__ == "__main__":
    migrate_data() 