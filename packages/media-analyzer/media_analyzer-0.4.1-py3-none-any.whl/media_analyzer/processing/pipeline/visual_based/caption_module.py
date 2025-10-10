from PIL.Image import Image

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import CaptionData, FrameData
from media_analyzer.machine_learning.caption.captioner_protocol import CaptionerProtocol
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


# pylint: disable-next = too-many-statements
def analyze_image(captioner: CaptionerProtocol, image: Image) -> CaptionData:
    """Analyzes an image by asking a series of questions."""

    # Helper function to ask a question and get a response
    def ask(question: str) -> str:
        return captioner.caption(image, instruction=question)

    # --- Use Case 1: Default caption ---
    default_caption = captioner.caption(image)

    # --- Ask all questions and gather raw answers ---
    main_subject = ask("Question: What is the single main subject of this photo? Answer:")
    in_or_outdoors_raw = ask("Question: Is this photo taken indoors or outdoors? Answer:")

    is_landscape = None
    is_cityscape = None
    if "outdoor" in in_or_outdoors_raw.lower():
        is_landscape_raw = ask(
            "Question: Is this a landscape featuring natural scenery such as "
            "mountains, dunes, forests, lakes, etc.? yes or no. Answer:"
        )
        is_landscape = "yes" in is_landscape_raw.lower()
        is_cityscape_raw = ask(
            "Question: Is this a cityscape showing urban buildings, "
            "streets, skylines, etc.? yes or no. Answer:"
        )
        is_cityscape = "yes" in is_cityscape_raw.lower()

    has_pet_raw = ask("Question: Does this photo contain one or more pets? yes or no. Answer:")
    pet_type = None
    has_animals = None
    animal_type = None
    if "yes" in has_pet_raw.lower():
        pet_type = ask("Question: What kind of pet is shown in this photo? Answer:")
    else:
        has_animals_raw = ask(
            "Question: Does this photo contain one or more live animals? yes or no. Answer:"
        )
        has_animals = "yes" in has_animals_raw.lower()
        if has_animals:
            animal_type = ask("Question: What animal is shown in this photo? Answer:")

    is_food_raw = ask("Question: Is this a photo of food or drink? yes or no. Answer:")
    food_type = None
    if "yes" in is_food_raw.lower():
        food_type = ask("Question: What kind of food is this? Answer:")

    has_vehicle_raw = ask(
        "Question: Is there a vehicle shown prominently in this photo? yes or no. Answer:"
    )
    vehicle_type = None
    if "yes" in has_vehicle_raw.lower():
        vehicle_type = ask(
            "Question: What type of vehicle is in this image (e.g., car, boat, bicycle)? Answer:"
        )

    setting = ask("Question: What is the setting of this photo? Answer:")

    is_event_raw = ask(
        "Question: Does this photo appear to be from a specific event "
        "(e.g., birthday party, wedding, concert, holiday)? Answer yes or no. Answer:"
    )
    event_type = None
    if "yes" in is_event_raw.lower():
        event_type = ask("Question: What event is depicted in this photo? Answer:")

    has_landmarks_raw = ask(
        "Question: Are there any recognizable landmarks or famous places in this photo? "
        "Answer yes or no. Answer:"
    )
    landmark_name = None
    if "yes" in has_landmarks_raw.lower():
        landmark_name = ask(
            "Question: What landmark or famous place is shown in this photo? Answer:"
        )

    is_document_raw = ask(
        "Question: Is this a photo of a document, like a "
        "passport, receipt, ticket, book, magazine, notes, payment card, "
        "id card, menu, or recipe? Answer yes or no. Answer:"
    )
    document_type = None
    if "yes" in is_document_raw.lower():
        document_type = ask("Question: What kind of document is this? Answer:")

    has_people_raw = ask(
        "Question: Does this photo contain one or more people? Answer yes or no. Answer:"
    )
    people_count = None
    people_mood = None
    photo_type = None
    if "yes" in has_people_raw.lower():
        people_count_raw = ask(
            "Question: How many people are in this photo? Answer with a number. Answer:"
        )
        try:
            # A simple attempt to parse a number from the response
            people_count = int("".join(filter(str.isdigit, people_count_raw)))
        except (ValueError, TypeError):
            people_count = None  # Could not parse an integer

        people_mood = ask(
            "Question: What is the overall mood of the people in this photo? "
            "Are they happy, sad, serious, or neutral? Answer:"
        )
        photo_type = ask(
            "Question: What kind of photo is this, choose one of: "
            "(selfie, group photo, crowd, portrait, other). Answer:"
        )

    activity_description = None
    is_activity_raw = ask("Question: Is an activity being performed in this photo? Answer:")
    is_activity = "yes" in is_activity_raw.lower()
    if is_activity:
        activity_description = ask(
            "Question: What activity is being performed in this photo? Answer:"
        )

    # --- Populate the model ---
    return CaptionData(
        default_caption=default_caption,
        main_subject=main_subject,
        is_indoor="indoor" in in_or_outdoors_raw.lower(),
        is_landscape=is_landscape,
        is_cityscape=is_cityscape,
        contains_pets="yes" in has_pet_raw.lower(),
        pet_type=pet_type,
        contains_animals=has_animals,
        animal_type=animal_type,
        is_food_or_drink="yes" in is_food_raw.lower(),
        food_or_drink_type=food_type,
        contains_vehicle="yes" in has_vehicle_raw.lower(),
        vehicle_type=vehicle_type,
        setting=setting,
        is_event="yes" in is_event_raw.lower(),
        event_type=event_type,
        contains_landmarks="yes" in has_landmarks_raw.lower(),
        landmark_name=landmark_name,
        is_document="yes" in is_document_raw.lower(),
        document_type=document_type,
        contains_people="yes" in has_people_raw.lower(),
        people_count=people_count,
        people_mood=people_mood,
        photo_type=photo_type,
        is_activity=is_activity,
        activity_description=activity_description,
    )


class CaptionModule(PipelineModule[FrameData]):
    """Generate a caption from an image."""

    def process(self, data: FrameData, config: FullAnalyzerConfig) -> None:
        """Generate caption data from an image."""
        data.caption_data = analyze_image(config.captioner, data.image)
