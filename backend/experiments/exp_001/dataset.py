import uuid

from domain.entities.document import Document

DOCUMENTS_DATASET = [
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The company faced declining revenue for three consecutive quarters. "
            "During the same period, customer churn increased while marketing spend remained flat. "
            "As a result, management concluded that the revenue decline was driven more by retention issues than by lack of customer acquisition."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The river flooded the surrounding farmland after unusually heavy rainfall upstream. "
            "Because the levees had not been reinforced since their construction decades earlier, "
            "they failed to contain the increased water volume."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The experiment was repeated under identical conditions, except that the temperature was lowered by five degrees. "
            "Only in the lower-temperature trials did the compound crystallize, suggesting temperature was a necessary condition for crystallization."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The city expanded public transit access to underserved neighborhoods. "
            "Within a year, employment rates in those areas increased. "
            "City officials attributed the employment gains to improved access to job centers."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The software update reduced memory usage but introduced longer load times. "
            "User complaints shifted from application crashes to performance delays, "
            "indicating that stability improvements came at the cost of responsiveness."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "Initially, the policy aimed to reduce emissions through voluntary compliance. "
            "After emissions remained unchanged, enforcement mechanisms were added. "
            "Following enforcement, emissions declined significantly."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The historian notes that the state lacked natural defenses and had limited military resources. "
            "Surrounded by rival powers, it sought security through diplomatic alliances rather than territorial expansion."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The study group that met weekly showed steady improvement in test scores. "
            "A control group studying individually showed no comparable gains. "
            "Researchers inferred that collaborative learning contributed to improved performance."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "When raw material costs increased, the manufacturer raised prices. "
            "Sales volume subsequently declined, but total revenue remained stable, "
            "implying that price increases offset reduced demand."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The startup prioritized rapid user growth over immediate profitability. "
            "Although losses accumulated initially, the expanded user base later enabled successful monetization."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The region depended heavily on agriculture, which suffered during prolonged drought. "
            "As crop yields fell, food prices rose, leading to increased migration to urban areas."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The algorithm performed well on training data but poorly on unseen examples. "
            "After reducing model complexity, performance on new data improved, "
            "suggesting the original model suffered from overfitting."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The organization decentralized decision-making authority. "
            "Teams responded faster to market changes, but inconsistencies across regions increased, "
            "highlighting a trade-off between agility and uniformity."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "Because funding was delayed, the infrastructure project missed its initial deadlines. "
            "Compressed timelines later increased costs due to expedited labor and materials."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The novel was initially criticized for its unconventional structure. "
            "Over time, academic analysis reframed those same features as innovative, "
            "leading to its eventual inclusion in literary curricula."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The country faced international sanctions that limited access to foreign capital. "
            "Domestic industries expanded to compensate, resulting in reduced reliance on imports."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The teacher replaced lectures with problem-based learning. "
            "Although students struggled at first, long-term retention improved, "
            "suggesting initial difficulty supported deeper understanding."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "After automating routine tasks, the company reduced staffing levels. "
            "Remaining employees focused on higher-value work, increasing overall productivity."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "The ecosystem lost its top predator due to overhunting. "
            "Herbivore populations expanded unchecked, leading to vegetation decline."
        ),
    ),
    Document(
        id=str(uuid.uuid4()),
        text=(
            "Early reports underestimated the severity of the outbreak due to limited testing. "
            "As testing capacity expanded, case counts rose sharply without a corresponding increase in mortality rate."
        ),
    ),
]
