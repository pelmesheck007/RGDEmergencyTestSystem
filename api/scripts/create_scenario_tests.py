from api.models.scenario_tests import ScenarioTest, ScenarioStep, ScenarioChoice, ScenarioLog

def create_scenario_tests(db, student, themes):
    theme1, theme2, theme3 = themes

    # Первый тест - расширенный
    scenario = ScenarioTest(
        title="Отказ светофора на перегоне",
        description="Пошаговая проверка реакции на отказ сигнализации светофора на железнодорожном перегоне",
        theme_id=theme1.id
    )
    db.add(scenario)
    db.flush()

    # Шаги первого сценария
    step1 = ScenarioStep(
        scenario_id=scenario.id,
        text="Светофор не работает. Ваши действия?",
        is_final=False,
        order=1
    )
    step2 = ScenarioStep(
        scenario_id=scenario.id,
        text="Как вы обеспечите безопасность движения на перегоне?",
        is_final=False,
        order=2
    )
    step3 = ScenarioStep(
        scenario_id=scenario.id,
        text="Кому вы сообщаете о возникшей ситуации?",
        is_final=False,
        order=3
    )
    step_final = ScenarioStep(
        scenario_id=scenario.id,
        text="Ситуация локализована, движение восстановлено. Сценарий завершён.",
        is_final=True,
        order=4
    )

    db.add_all([step1, step2, step3, step_final])
    db.flush()

    # Выборы для первого сценария
    db.add_all([
        ScenarioChoice(step_id=step1.id, choice_text="Остановить поезд и уведомить диспетчера", next_step_id=step2.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=step1.id, choice_text="Игнорировать и продолжить движение", next_step_id=step_final.id,
                       is_critical_error=True),

        ScenarioChoice(step_id=step2.id, choice_text="Организовать ручное регулирование движения", next_step_id=step3.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=step2.id, choice_text="Продолжить движение с осторожностью", next_step_id=step_final.id,
                       is_critical_error=True),

        ScenarioChoice(step_id=step3.id, choice_text="Сообщить дежурному по станции", next_step_id=step_final.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=step3.id, choice_text="Сообщить сменщику поезда", next_step_id=step_final.id,
                       is_critical_error=True),
    ])
    db.flush()

    # Второй тест - новая ситуация на ж/д
    scenario2 = ScenarioTest(
        title="Авария на железнодорожном переезде",
        description="Действия при столкновении поезда с автомобилем на переезде",
        theme_id=theme2.id
    )
    db.add(scenario2)
    db.flush()

    s2_step1 = ScenarioStep(
        scenario_id=scenario2.id,
        text="Поезд столкнулся с автомобилем на переезде. Ваши первые действия?",
        is_final=False,
        order=1
    )
    s2_step2 = ScenarioStep(
        scenario_id=scenario2.id,
        text="Как вы оцениваете состояние пострадавших?",
        is_final=False,
        order=2
    )
    s2_step3 = ScenarioStep(
        scenario_id=scenario2.id,
        text="Кому и как вы сообщаете об аварии?",
        is_final=False,
        order=3
    )
    s2_final = ScenarioStep(
        scenario_id=scenario2.id,
        text="Авария обработана, движение восстановлено. Сценарий завершён.",
        is_final=True,
        order=4
    )
    db.add_all([s2_step1, s2_step2, s2_step3, s2_final])
    db.flush()

    # Выборы для второго сценария
    db.add_all([
        ScenarioChoice(step_id=s2_step1.id, choice_text="Остановить поезд и вызвать экстренные службы", next_step_id=s2_step2.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=s2_step1.id, choice_text="Продолжить движение, не уведомляя никого", next_step_id=s2_final.id,
                       is_critical_error=True),

        ScenarioChoice(step_id=s2_step2.id, choice_text="Проверить состояние водителя автомобиля", next_step_id=s2_step3.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=s2_step2.id, choice_text="Игнорировать состояние пострадавших", next_step_id=s2_final.id,
                       is_critical_error=True),

        ScenarioChoice(step_id=s2_step3.id, choice_text="Сообщить диспетчеру и полиции", next_step_id=s2_final.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=s2_step3.id, choice_text="Сообщить только начальнику поезда", next_step_id=s2_final.id,
                       is_critical_error=True),
    ])
    db.flush()

    # Пример логов прохождения для первого сценария
    db.add_all([
        ScenarioLog(user_id=student.id, scenario_id=scenario.id, step_id=step1.id, choice_id=step1.choices[0].id,
                    time_taken=15),
        ScenarioLog(user_id=student.id, scenario_id=scenario.id, step_id=step2.id, choice_id=step2.choices[0].id,
                    time_taken=20),
        ScenarioLog(user_id=student.id, scenario_id=scenario.id, step_id=step3.id, choice_id=step3.choices[0].id,
                    time_taken=10)
    ])
    db.flush()
