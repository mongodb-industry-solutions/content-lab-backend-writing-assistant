import asyncio
import json
import os
import sys

# Add parent directory to path only once
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bson import ObjectId
from db.mdb import MongoDBConnector
from writing_assistant.assistant import WritingAssistant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB collection name from env or use default
USER_PROFILES_COLLECTION = os.getenv("USER_PROFILES_COLLECTION", "userProfiles")


async def test_writing_tools():
    # Initialize MongoDB connection
    mongo_client = MongoDBConnector()
    profiles_collection = mongo_client.get_collection(USER_PROFILES_COLLECTION)
    
    # Fetch all available profiles
    profiles = list(profiles_collection.find())
    
    if not profiles:
        print("No profiles found in the database. Please add some profiles first.")
        return
        
    # Convert ObjectId to string for each profile
    for profile in profiles:
        profile["id"] = str(profile.pop("_id"))
    
    # Display available profiles for selection
    print("Available profiles:")
    for i, profile in enumerate(profiles):
        print(f"{i+1}. {profile.get('persona', 'Unnamed')} - {profile.get('tone', 'No tone')}")
    
    # Initialize the writing assistant
    assistant = WritingAssistant()
    
    print("\n---- Testing Writing Assistant with Database Profiles \n")
    
    try:
        # For this test, we'll use the first 3 profiles
        formal_profile = profiles[0] if len(profiles) > 0 else None
        casual_profile = profiles[1] if len(profiles) > 1 else formal_profile
        third_profile = profiles[2] if len(profiles) > 2 else casual_profile
        
        if formal_profile:
            # Test 1: Create an outline using the first profile
            print(f" Test 1: CREATE OUTLINE ({formal_profile.get('persona', 'Profile 1')}) ===")
            outline_topic = "The Impact of Artificial Intelligence on Modern Healthcare"
            outline_brief = "A comprehensive analysis of how AI technologies are transforming diagnosis, treatment, and patient care in the medical field."
            
            outline_result = await assistant.process_request(
                user_input="I need to create a structured outline for my paper",
                content=outline_topic,
                user_profile=formal_profile,
                selected_tool="outline",  
                topic_details="Focus on both benefits and ethical concerns",
                brief=outline_brief
            )
            
            print(f"Profile Used: {outline_result['profile_used']}")
            print(f"Tool Used: {outline_result['tool_used']}")
            print("\nOutline Structure:")
            print(json.dumps(outline_result['result']['outline_structure'], indent=2))
            print("\nMain Points:")
            for point in outline_result['result']['main_points']:
                print(f"- {point}")
        
        if casual_profile:    
            # Test 2: Refine content using the second profile
            print(f"\n--- TEST 2: REFINE CONTENT ({casual_profile.get('persona', 'Profile 2')}) --- ")
            rough_content = """
            AI is changing healthcare in many important ways. First, it helps doctors diagnose diseases faster and more accurately using advanced algorithms. Second, it improves treatment plans by analyzing patient data and medical research. Third, it enhances patient monitoring through wearable devices and remote sensors. However, there are also concerns about data privacy and the role of human judgment in medical decisions.
            """
            
            refine_result = await assistant.process_request(
                user_input="Make this content more engaging and stylish",
                content=rough_content,
                user_profile=casual_profile,
                selected_tool="refine",  
                topic_details="This is for a blog aimed at young adults interested in technology and healthcare"
            )
            
            print(f"Profile Used: {refine_result['profile_used']}")
            print(f"Tool Used: {refine_result['tool_used']}")
            print("\nRefined Content:")
            print(refine_result['result']['refined_content'])
            print("\nStyle Changes:")
            for change in refine_result['result']['style_changes']:
                print(f"- {change}")
            
            # Save the refined content for the proofread test
            refined_content = refine_result['result']['refined_content']
            
            if third_profile:
                # Test 3: Proofread content using the third profile
                print(f"\n ---- TEST 3: PROOFREAD CONTENT ({third_profile.get('persona', 'Profile 3')}) ")
                
                # Add some deliberate errors to the refined content
                content_with_errors = refined_content.replace("healthcare", "heath care")
                content_with_errors = content_with_errors.replace("doctors", "doctor's")
                content_with_errors = content_with_errors.replace("decisions", "desicions")
                
                proofread_result = await assistant.process_request(
                    user_input="Check this for grammar and spelling errors",
                    content=content_with_errors,
                    user_profile=third_profile,
                    selected_tool="proofread"  # Direct tool selection
                )
                
                print(f"Profile Used: {proofread_result['profile_used']}")
                print(f"Tool Used: {proofread_result['tool_used']}")
                print(f"\nError Count: {proofread_result['result']['error_count']}")
                print("\nCorrections:")
                for correction in proofread_result['result']['corrections']:
                    print(f"- {correction}")
                print("\nImproved Text:")
                print(proofread_result['result']['improved_text'])
        
        # Test 4: Chat completion (no tool selected - should use chat)
        print("\n TEST 4: CHAT COMPLETION (NO TOOL SELECTED) ")
        chat_result = await assistant.process_request(
            user_input="Explain the benefits of AI in healthcare in a simple way",
            content="",
            user_profile=formal_profile,
            selected_tool=None  # No tool selected
        )
        
        print(f"Profile Used: {chat_result['profile_used']}")
        print(f"Tool Used: {chat_result['tool_used']}")
        print("\nChat Response:")
        print(chat_result['result']['response'])
        
        # Test 5: Invalid tool selection (should return error)
        print("\n TEST 5: INVALID TOOL SELECTION (SHOULD RETURN ERROR)")
        invalid_tool_result = await assistant.process_request(
            user_input="Can you help me with this content?",
            content="Some sample content",
            user_profile=formal_profile,
            selected_tool="invalid_tool"  # Invalid tool name
        )
        
        print("Error Status:", invalid_tool_result.get("status"))
        print("Error Message:", invalid_tool_result.get("error"))
        print("Available Tools:", invalid_tool_result.get("available_tools"))
                
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        # Close MongoDB connection if needed
        if hasattr(mongo_client, 'close'):
            mongo_client.close()

if __name__ == "__main__":
    asyncio.run(test_writing_tools())