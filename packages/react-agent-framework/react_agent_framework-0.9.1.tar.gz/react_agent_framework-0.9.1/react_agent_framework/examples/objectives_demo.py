"""
Objectives system demonstration

Shows how to use objectives for goal-oriented agents
"""

from datetime import datetime, timedelta
from react_agent_framework import ReactAgent
from react_agent_framework.core.objectives import Objective, ObjectiveTracker


def demo_basic_objectives():
    """Demo 1: Basic objective tracking"""
    print("=" * 80)
    print("DEMO 1: BASIC OBJECTIVES")
    print("=" * 80)

    # Create objectives
    obj1 = Objective(
        goal="Research Python frameworks",
        success_criteria=["Find 3+ frameworks", "Compare features"],
        priority="high",
    )

    obj2 = Objective(
        goal="Write documentation",
        success_criteria=["Create README", "Add examples"],
        priority="medium",
        deadline=datetime.now() + timedelta(days=7),
    )

    obj3 = Objective(
        goal="Deploy to production",
        success_criteria=["Pass all tests", "Deploy successfully"],
        priority="critical",
    )

    # Create tracker
    tracker = ObjectiveTracker()
    tracker.add(obj1)
    tracker.add(obj2)
    tracker.add(obj3)

    print("\n" + tracker.get_summary())

    # Start working on next objective
    print("\n\n🎯 Starting next objective...")
    next_obj = tracker.start_next()
    print(f"Started: {next_obj}")

    # Update progress
    print("\n📈 Updating progress...")
    tracker.update_progress(next_obj.id, 0.5, "Found 2 frameworks so far")
    print(f"Progress: {next_obj.progress:.0%}")

    # Complete objective
    print("\n✅ Completing objective...")
    tracker.complete(next_obj.id, "Research completed successfully")
    print(tracker.get_summary())


def demo_agent_with_objectives():
    """Demo 2: Agent with objectives"""
    print("\n" + "=" * 80)
    print("DEMO 2: AGENT WITH OBJECTIVES")
    print("=" * 80)

    # Create objectives
    objectives = [
        Objective(
            goal="Calculate the total cost of purchasing 15 items at $8.99 each",
            success_criteria=["Perform calculation", "Provide final total"],
            priority="high",
        ),
        Objective(
            goal="Research AI agent frameworks",
            success_criteria=["Find examples", "Compare approaches"],
            priority="medium",
        ),
    ]

    # Create agent with objectives
    agent = ReactAgent(
        name="Goal-Oriented Assistant",
        provider="gpt-4o-mini",
        objectives=objectives,
    )

    # Add calculator tool
    @agent.tool()
    def calculate(expression: str) -> str:
        """Calculate mathematical expressions"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

    print("\n📋 Agent Objectives:")
    print(agent.objectives.get_summary())

    print("\n\n🤔 Running agent...")
    answer = agent.run("Calculate 15 * 8.99", verbose=False)
    print(f"\nAnswer: {answer}")

    # Mark objective as completed
    first_obj = agent.objectives.get_active()[0] if agent.objectives.get_active() else None
    if first_obj:
        agent.objectives.complete(first_obj.id, "Calculation completed successfully")

    print("\n\n📊 Updated Objectives:")
    print(agent.objectives.get_summary())


def demo_objective_priorities():
    """Demo 3: Priority-based objective management"""
    print("\n" + "=" * 80)
    print("DEMO 3: PRIORITY MANAGEMENT")
    print("=" * 80)

    tracker = ObjectiveTracker()

    # Add objectives with different priorities
    tracker.create(
        goal="Fix critical security bug",
        priority="critical",
        deadline=datetime.now() + timedelta(hours=2),
    )

    tracker.create(
        goal="Update documentation",
        priority="low",
        deadline=datetime.now() + timedelta(days=30),
    )

    tracker.create(
        goal="Implement new feature",
        priority="high",
        deadline=datetime.now() + timedelta(days=7),
    )

    tracker.create(
        goal="Code review",
        priority="medium",
        deadline=datetime.now() + timedelta(days=3),
    )

    print("\n📋 All Objectives:")
    for obj in tracker.objectives.values():
        print(f"  {obj}")

    print("\n\n🎯 Priority Order:")
    print(f"Next to work on: {tracker.get_next()}")

    # Start working through objectives
    print("\n\n🔄 Processing objectives by priority...")
    while tracker.get_pending():
        obj = tracker.start_next()
        print(f"\nStarted: {obj.goal}")
        print(f"  Priority: {obj.priority.value}")
        print(f"  Deadline: {obj.deadline.strftime('%Y-%m-%d %H:%M') if obj.deadline else 'None'}")

        # Simulate completion
        tracker.complete(obj.id, f"Completed {obj.goal}")

    print("\n\n✅ Final Status:")
    print(tracker.get_summary())


def demo_sub_objectives():
    """Demo 4: Sub-objectives and hierarchies"""
    print("\n" + "=" * 80)
    print("DEMO 4: SUB-OBJECTIVES")
    print("=" * 80)

    # Create main objective
    main_obj = Objective(
        goal="Build and deploy web application",
        priority="high",
    )

    # Add sub-objectives
    main_obj.add_sub_objective(
        Objective(
            goal="Design database schema",
            priority="high",
        )
    )

    main_obj.add_sub_objective(
        Objective(
            goal="Implement API endpoints",
            priority="high",
        )
    )

    main_obj.add_sub_objective(
        Objective(
            goal="Create frontend UI",
            priority="medium",
        )
    )

    main_obj.add_sub_objective(
        Objective(
            goal="Write tests",
            priority="high",
        )
    )

    print(f"\n🎯 Main Objective: {main_obj.goal}")
    print(f"\n📋 Sub-objectives ({len(main_obj.sub_objectives)}):")
    for i, sub_obj in enumerate(main_obj.sub_objectives, 1):
        print(f"  {i}. [{sub_obj.priority.value.upper()}] {sub_obj.goal}")

    # Update progress on sub-objectives
    print("\n\n🔄 Working on sub-objectives...")
    for sub_obj in main_obj.sub_objectives:
        sub_obj.start()
        sub_obj.update_progress(1.0, "Completed")
        print(f"  ✅ {sub_obj.goal}")

    # Calculate overall progress
    overall_progress = sum(s.progress for s in main_obj.sub_objectives) / len(
        main_obj.sub_objectives
    )
    print(f"\n📈 Overall Progress: {overall_progress:.0%}")


def demo_objective_persistence():
    """Demo 5: Save and load objectives"""
    print("\n" + "=" * 80)
    print("DEMO 5: OBJECTIVE PERSISTENCE")
    print("=" * 80)

    # Create tracker with objectives
    tracker = ObjectiveTracker()
    tracker.create(
        goal="Complete project milestone",
        success_criteria=["Finish all tasks", "Deploy to staging"],
        priority="high",
    )
    tracker.create(
        goal="Review pull requests",
        priority="medium",
    )

    print("\n📋 Original Tracker:")
    print(tracker.get_summary())

    # Save to dict
    tracker_data = tracker.to_dict()
    print(f"\n💾 Saved {len(tracker_data['objectives'])} objectives")

    # Load from dict
    new_tracker = ObjectiveTracker.from_dict(tracker_data)

    print("\n📋 Loaded Tracker:")
    print(new_tracker.get_summary())

    print("\n✅ Objectives preserved!")


def main():
    """Run all demos"""
    print("\n🎯 OBJECTIVES SYSTEM DEMONSTRATION\n")

    # Demo 1: Basic objectives
    demo_basic_objectives()

    # Demo 2: Agent with objectives
    demo_agent_with_objectives()

    # Demo 3: Priority management
    demo_objective_priorities()

    # Demo 4: Sub-objectives
    demo_sub_objectives()

    # Demo 5: Persistence
    demo_objective_persistence()

    print("\n" + "=" * 80)
    print("✅ All demos completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
