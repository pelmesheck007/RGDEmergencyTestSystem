from api.models.scenario_tests import ScenarioTest, ScenarioStep, ScenarioChoice, ScenarioLog




def create_scenario_tests(db, student, themes):
    theme1, theme2, theme3 = themes
    scenario = ScenarioTest(
        title="Отказ светофора на перегоне",
        description="Пошаговая проверка реакции на отказ сигнализации",
        theme_id=theme1.id
    )
    db.add(scenario)
    db.flush()

    step1 = ScenarioStep(
        scenario_id=scenario.id,
        text="Светофор не работает. Ваши действия?",
        is_final=False
    )
    step2 = ScenarioStep(
        scenario_id=scenario.id,
        text="Кому вы сообщаете о ситуации?",
        is_final=False
    )
    step_final = ScenarioStep(
        scenario_id=scenario.id,
        text="Ситуация локализована. Поезд остановлен. Сценарий завершён.",
        is_final=True
    )

    db.add_all([step1, step2, step_final])
    db.flush()

    # Choices
    db.add_all([
        ScenarioChoice(step_id=step1.id, choice_text="Сообщить дежурному по станции", next_step_id=step2.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=step1.id, choice_text="Проигнорировать и двигаться дальше", next_step_id=step_final.id,
                       is_critical_error=True),
        ScenarioChoice(step_id=step2.id, choice_text="Диспетчеру участка", next_step_id=step_final.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=step2.id, choice_text="Сменщику", next_step_id=step_final.id, is_critical_error=True)
    ])
    db.flush()

    scenario2 = ScenarioTest(
        title="Авария на химическом заводе",
        description="Действия в случае утечки опасного вещества",
        theme_id=theme2.id
    )
    db.add(scenario2)
    db.flush()

    s2_step1 = ScenarioStep(scenario_id=scenario2.id, text="Вы заметили запах газа. Что делаете?", is_final=False)
    s2_step2 = ScenarioStep(scenario_id=scenario2.id, text="Куда направляетесь?", is_final=False)
    s2_final = ScenarioStep(scenario_id=scenario2.id, text="Вы эвакуировались. Сценарий завершен.", is_final=True)
    db.add_all([s2_step1, s2_step2, s2_final])
    db.flush()

    db.add_all([
        ScenarioChoice(step_id=s2_step1.id, choice_text="Сообщить диспетчеру", next_step_id=s2_step2.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=s2_step1.id, choice_text="Игнорировать", next_step_id=s2_final.id,
                       is_critical_error=True),
        ScenarioChoice(step_id=s2_step2.id, choice_text="Эвакуационный выход", next_step_id=s2_final.id,
                       is_critical_error=False),
        ScenarioChoice(step_id=s2_step2.id, choice_text="К подвалу", next_step_id=s2_final.id,
                       is_critical_error=True)
    ])

    # Scenario log (симуляция прохождения)
    db.add_all([
        ScenarioLog(user_id=student.id, scenario_id=scenario.id, step_id=step1.id, choice_id=step1.choices[0].id,
                    time_taken=10),
        ScenarioLog(user_id=student.id, scenario_id=scenario.id, step_id=step2.id, choice_id=step2.choices[0].id,
                    time_taken=8)
    ])