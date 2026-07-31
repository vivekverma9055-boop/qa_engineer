from django.core.management.base import BaseCommand

from chatbot.models import KnowledgeBase

ENTRIES = [
    {
        "question": "What kind of testing do you do?",
        "keywords": "services, offer, capabilities, what do you do",
        "answer": (
            "I cover manual and automated testing across web apps, desktop UI, Android & iOS "
            "mobile apps, APIs/backends, and physical devices (cameras, VoIP/telecom hardware, "
            "IoT). That includes functional, regression, UI, integration, and exploratory testing."
        ),
    },
    {
        "question": "Do you test iOS apps and devices?",
        "keywords": "ios, iphone, ipad, apple, xcode, xcuitest",
        "answer": (
            "Yes. Alongside Android automation with Appium, I test iOS apps and devices — "
            "installing/validating builds on real hardware, functional and regression passes, "
            "and Appium/XCUITest-based automation where a project needs it."
        ),
    },
    {
        "question": "Can you test physical hardware or camera devices?",
        "keywords": "hardware, camera, device lab, physical device, firmware, iot",
        "answer": (
            "Yes — I've automated end-to-end testing on Android-based VoIP/telecom hardware "
            "(call workflows, audio, firmware regression) and I'm comfortable extending that to "
            "other connected devices and camera hardware: connectivity, real-world workflow "
            "testing, and regression across firmware releases."
        ),
    },
    {
        "question": "Do you work with clients in the US, UK, or other countries?",
        "keywords": "us, uk, canada, timezone, international, remote, overseas client",
        "answer": (
            "Yes, I work remotely with clients worldwide and keep flexible hours to overlap "
            "with US/UK/EU time zones for calls and hand-offs."
        ),
    },
    {
        "question": "What are your rates / how much do you charge?",
        "keywords": "price, pricing, cost, rate, budget, hourly",
        "answer": (
            "Rates depend on project scope (manual testing vs. building a full automation "
            "framework, one-off vs. ongoing). Share your project details in the contact form "
            "and I'll follow up with a custom quote — hourly, fixed-scope, and monthly retainer "
            "options are all available."
        ),
    },
    {
        "question": "How do we get started working together?",
        "keywords": "start, begin, onboarding, process, kick off",
        "answer": (
            "Send your project details through the contact form (or email me directly). We'll "
            "have a short discovery call to scope the testing needed, I'll share a test plan/"
            "estimate, and once approved we move into execution with regular status updates."
        ),
    },
    {
        "question": "What automation tools and languages do you use?",
        "keywords": "selenium, appium, python, pytest, tools, tech stack, framework",
        "answer": (
            "Python for automation code, Selenium WebDriver for web, Appium for Android/iOS "
            "mobile and device automation, and Pytest as the test runner — plus Postman for API "
            "testing and Git/Bitbucket for version control."
        ),
    },
    {
        "question": "Do you also do manual testing, or only automation?",
        "keywords": "manual testing, exploratory, test cases",
        "answer": (
            "Both. Many engagements start with manual/exploratory testing and PRD-based test "
            "case design, then move into automation for the regression-prone parts once the "
            "feature has stabilized."
        ),
    },
    {
        "question": "Can you validate backend data and APIs, not just the UI?",
        "keywords": "api testing, backend, database, mongodb, sql, postman",
        "answer": (
            "Yes — API testing with Postman (status codes, payloads, edge cases) plus backend "
            "data validation in MongoDB and SQL to make sure what the UI shows actually matches "
            "what's stored and processed correctly."
        ),
    },
    {
        "question": "Do you sign NDAs or work under contract?",
        "keywords": "nda, contract, confidentiality, agreement",
        "answer": (
            "Yes, I'm happy to sign an NDA and work under whatever contract structure your "
            "company requires before any project details are shared."
        ),
    },
    {
        "question": "How much experience do you have?",
        "keywords": "experience, years, background, istqb, certified",
        "answer": (
            "I have 2+ years as a QA Automation Engineer / SDET across product and enterprise "
            "teams, and I'm ISTQB Certified Tester Foundation Level (CTFL)."
        ),
    },
    {
        "question": "Do you provide test reports and documentation?",
        "keywords": "report, documentation, test plan, deliverable",
        "answer": (
            "Yes — every engagement includes a test plan/strategy up front and clear "
            "documentation of results, defects found, and coverage at the end, so you always "
            "know exactly what was tested and what wasn't."
        ),
    },
    {
        "question": "How soon can you start a project?",
        "keywords": "availability, start date, timeline, when can you start, turnaround",
        "answer": (
            "I'm currently accepting new projects and can typically kick off within a few days "
            "of the scope being confirmed."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed the chatbot's knowledge base with common freelance-QA questions and answers."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for entry in ENTRIES:
            obj, was_created = KnowledgeBase.objects.update_or_create(
                question=entry["question"],
                defaults={"keywords": entry["keywords"], "answer": entry["answer"], "is_published": True},
            )
            created += int(was_created)
            updated += int(not was_created)
        self.stdout.write(self.style.SUCCESS(f"Knowledge base seeded: {created} created, {updated} updated."))
