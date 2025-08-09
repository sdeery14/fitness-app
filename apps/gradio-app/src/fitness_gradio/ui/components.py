"""
UI components for the fitness app.
"""
import gradio as gr
from typing import List, Any
from datetime import date

from fitness_core.agents import FitnessAgent
from fitness_core.agents.providers import ModelProvider
from .styles import (
    HEADER_MARKDOWN, 
    HELP_CONTENT, 
    MODEL_COMPARISON_CONTENT, 
    EXAMPLE_PROMPTS
)


class UIComponents:
    """Factory class for creating UI components."""
    
    @staticmethod
    def create_header() -> gr.Markdown:
        """Create the app header."""
        return gr.Markdown(HEADER_MARKDOWN)
    
    @staticmethod
    def create_model_selection_section() -> tuple:
        """
        Create the model selection section with dropdown.
        
        Returns:
            Tuple of (model_dropdown, selected_model)
        """
        with gr.Column():
            gr.Markdown("### 🤖 AI Model Selection")
            
            # Get model data and organize by provider
            table_data = FitnessAgent.get_models_table_data()
            
            # Organize models by provider
            anthropic_models = []
            openai_models = []
            groq_models = []
            
            for row in table_data:
                star, provider, model_name, capability, speed, cost, description = row
                
                # Extract provider information and create display text
                if "Anthropic" in provider:
                    display_text = f"{model_name} (Anthropic)"
                    anthropic_models.append((display_text, model_name))
                elif "OpenAI" in provider and "via Groq" not in provider:
                    display_text = f"{model_name} (OpenAI)"
                    openai_models.append((display_text, model_name))
                elif "via Groq" in provider:
                    # Only include text generation models from Groq (exclude Whisper speech-to-text models)
                    if model_name.startswith("whisper"):
                        continue  # Skip Whisper models as they are speech-to-text, not text generation
                    
                    # Extract the actual provider (Meta, Google, etc.) from the provider string
                    if "Meta" in provider:
                        display_text = f"{model_name} (Meta via Groq)"
                    elif "Google" in provider:
                        display_text = f"{model_name} (Google via Groq)"
                    elif "Mistral" in provider:
                        display_text = f"{model_name} (Mistral via Groq)"
                    elif "Alibaba" in provider:
                        display_text = f"{model_name} (Alibaba via Groq)"
                    elif "Moonshot" in provider:
                        display_text = f"{model_name} (Moonshot via Groq)"
                    elif "OpenAI" in provider:
                        display_text = f"{model_name} (OpenAI via Groq)"
                    else:
                        display_text = f"{model_name} (Groq)"
                    groq_models.append((display_text, model_name))
                else:
                    # Fallback for unknown providers
                    display_text = f"{model_name} (Unknown)"
                    openai_models.append((display_text, model_name))
            
            # Sort within each provider by model size (largest to smallest)
            # Define model hierarchy for sorting
            model_order = {
                # Anthropic models (largest to smallest)
                "claude-4-opus": 0,
                "claude-4-sonnet": 1,
                "claude-3.7-sonnet": 2,
                "claude-3.5-sonnet-latest": 3,
                "claude-3.5-sonnet": 4,
                "claude-3.5-haiku": 5,
                "claude-3-haiku": 6,
                
                # OpenAI models (largest to smallest)
                "gpt-4o": 0,
                "gpt-4-turbo": 1,
                "gpt-4": 2,
                "gpt-4o-mini": 3,
                "gpt-3.5-turbo": 4,
                "o1-preview": 5,
                "o1-mini": 6,
                "o3-mini": 7,
                
                # Groq models (by capability and size - text generation only)
                "llama-3.3-70b-versatile": 0,
                "llama3-70b-8192": 1,
                "mixtral-8x7b-32768": 2,
                "qwen3-32b": 3,
                "kimi-k2-instruct": 4,
                "gemma2-9b-it": 5,
                "llama-3.1-8b-instant": 6,
                "llama3-8b-8192": 7,
                "gemma-7b-it": 8,
                "llama2-70b-4096": 9,
            }
            
            anthropic_models.sort(key=lambda x: model_order.get(x[1], 999))
            openai_models.sort(key=lambda x: model_order.get(x[1], 999))
            groq_models.sort(key=lambda x: model_order.get(x[1], 999))
            
            # Create final dropdown choices organized by provider
            dropdown_choices = []
            
            # Add Anthropic models first (alphabetically first)
            dropdown_choices.extend(anthropic_models)
            
            # Add Groq models (fast and cost-effective)
            dropdown_choices.extend(groq_models)
            
            # Add OpenAI models last
            dropdown_choices.extend(openai_models)
            
            # Get the configured default model from environment/config
            default_model = ModelProvider.resolve_model_name()
            
            # Main model selection dropdown (full width)
            model_dropdown = gr.Dropdown(
                choices=dropdown_choices,
                value=default_model,
                label="Select AI Model",
                info="Choose your preferred AI model for fitness guidance",
                elem_classes=["model-dropdown"]
            )
            
            # Hidden component to manage selection (for compatibility)
            selected_model = gr.Textbox(
                value=default_model,
                visible=False,
                label="Selected Model"
            )
        
        return model_dropdown, selected_model
    
    @staticmethod
    def create_chatbot() -> gr.Chatbot:
        """Create the main chatbot component."""
        return gr.Chatbot(
            elem_id="chatbot", 
            type="messages",
            show_copy_button=True,
            show_share_button=False,
            avatar_images=None,
            sanitize_html=True,
            render_markdown=True
        )
    
    @staticmethod
    def create_output_audio() -> gr.Audio:
        """Create the output audio component for TTS responses."""
        return gr.Audio(
            label="🔊 Audio Response", 
            streaming=False,  # Disable streaming to avoid ffmpeg issues
            autoplay=True,
            show_download_button=True,
            show_share_button=False,
            format="wav",  # Explicitly set format to WAV
            visible=False  # Initially hidden, will show when TTS is enabled
        )
    
    @staticmethod
    def create_chat_input() -> gr.MultimodalTextbox:
        """Create the chat input component."""
        return gr.MultimodalTextbox(
            interactive=True,
            file_count="multiple",
            placeholder="Ask me about fitness, request a workout plan, or get meal planning advice...",
            show_label=False,
            sources=["microphone", "upload"],  # Enable microphone and file uploads
            submit_btn=True,  # Ensure submit button is available
        )
    
    @staticmethod
    def create_control_buttons() -> tuple:
        """
        Create the control buttons (clear, streaming toggle, TTS toggle).
        
        Returns:
            Tuple of (clear_btn, streaming_toggle, tts_toggle)
        """
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Conversation", variant="secondary", size="sm")
            streaming_toggle = gr.Checkbox(
                label="🚀 Enable Real-time Streaming", 
                value=True, 
                info="Stream responses in real-time as the agent generates them"
            )
            tts_toggle = gr.Checkbox(
                label="🔊 Enable Text-to-Speech", 
                value=False, 
                info="Convert AI responses to speech using Groq's TTS models"
            )
        
        return clear_btn, streaming_toggle, tts_toggle
    
    @staticmethod
    def create_examples_section(chat_input: gr.MultimodalTextbox) -> gr.Examples:
        """Create the examples section."""
        with gr.Row():
            return gr.Examples(
                examples=EXAMPLE_PROMPTS,
                inputs=chat_input,
                label="💡 Try asking:"
            )
    
    @staticmethod
    def create_help_section() -> gr.Accordion:
        """Create the help accordion section."""
        with gr.Accordion("ℹ️ How to use this assistant", open=False):
            gr.Markdown(HELP_CONTENT)
    
    @staticmethod
    def create_model_comparison_section() -> gr.Accordion:
        """Create the model comparison accordion section."""
        with gr.Accordion("🤖 Model Comparison Guide", open=False):
            gr.Markdown(MODEL_COMPARISON_CONTENT)
    
    @staticmethod
    def create_voice_conversation_section() -> tuple:
        """
        Create the voice conversation section with controls and audio components.
        
        Returns:
            Tuple of (voice_btn, voice_status, voice_audio, voice_output, voice_exit_btn)
        """
        with gr.Row():
            gr.Markdown("### 🎙️ Voice Conversation")
        
        with gr.Row():
            voice_btn = gr.Button(
                "🎤 Start Voice Conversation", 
                variant="primary",
                size="lg"
            )
            voice_exit_btn = gr.Button(
                "❌ Exit Voice Chat", 
                variant="stop",
                size="lg",
                visible=False
            )
        
        # Voice conversation status indicator
        voice_status = gr.Markdown(
            value="",
            visible=False,
            elem_id="voice-status"
        )
        
        with gr.Row(visible=False, elem_id="voice-conversation-row") as voice_row:
            with gr.Column():
                # Audio input for voice conversation
                voice_audio = gr.Audio(
                    label="🎤 Voice Input",
                    sources=["microphone"],
                    type="numpy",
                    streaming=False,
                    waveform_options=gr.WaveformOptions(waveform_color="#B83A4B"),
                    elem_id="voice-audio"
                )
            
            with gr.Column():
                # Audio output for voice responses
                voice_output = gr.Audio(
                    label="🔊 AI Voice Response",
                    streaming=False,
                    autoplay=True,
                    show_download_button=True,
                    elem_id="voice-output"
                )
        
        # Voice conversation controls - removed separate voice_chatbot for unified approach
        
        return voice_btn, voice_status, voice_audio, voice_output, voice_exit_btn, voice_row

    @staticmethod
    def create_fitness_plan_section() -> tuple:
        """
        Create the fitness plan display section.
        
        Returns:
            Tuple of (plan_display, view_plan_btn, clear_plan_btn)
        """
        from fitness_core.agents.user_session import SessionManager
        
        # Get initial plan display content
        initial_content = UIComponents._get_initial_plan_content()
        
        # Create a scrollable fitness plan display similar to chatbot
        plan_display = gr.Markdown(
            value=initial_content,
            label="Current Fitness Plan",
            elem_id="fitness-plan-display",
            elem_classes=["fitness-plan-container"],
            show_label=False,  # Hide the label to save space
            container=True
        )
        
        with gr.Row(elem_classes=["fitness-plan-buttons"]):
            view_plan_btn = gr.Button(
                "📋 View Latest Plan", 
                variant="primary",
                size="sm",
                scale=1
            )
            clear_plan_btn = gr.Button(
                "🗑️ Clear Plan", 
                variant="secondary", 
                size="sm",
                scale=1
            )
        
        return plan_display, view_plan_btn, clear_plan_btn

    @staticmethod
    def _get_initial_plan_content() -> str:
        """Get initial content for the fitness plan display."""
        try:
            from fitness_core.agents.user_session import SessionManager
            
            session = SessionManager.get_current_session()
            if session and session.has_fitness_plan():
                plan = session.get_fitness_plan()
                if plan:
                    return UIComponents.format_structured_fitness_plan(plan)
            
            return "**No Fitness Plan Available**\n\nNo fitness plan has been generated yet. Ask me to create a personalized fitness plan for you!"
        except Exception as e:
            return f"**Error Loading Plan**\n\nThere was an error loading your fitness plan: {str(e)}"

    @staticmethod
    def format_structured_fitness_plan(plan_obj: Any) -> str:
        """
        Format a structured fitness plan object into a nicely formatted markdown string.
        
        Args:
            plan_obj: The fitness plan object with structured attributes
            
        Returns:
            Formatted markdown string
        """
        try:
            # Handle structured FitnessPlan object
            if hasattr(plan_obj, 'name') and hasattr(plan_obj, 'training_plan'):
                return UIComponents._format_fitness_plan_object(plan_obj)
            
            # Handle string representation of structured object
            elif isinstance(plan_obj, str) and 'training_plan_splits=' in plan_obj:
                return UIComponents._format_structured_plan_string(plan_obj)
            
            # Fallback to basic formatting
            else:
                return f"**Fitness Plan**\n\n{str(plan_obj)}"
                
        except Exception as e:
            return f"**Error Formatting Plan**\n\nSorry, there was an error formatting your fitness plan: {str(e)}"

    @staticmethod
    def _format_fitness_plan_object(plan_obj: Any) -> str:
        """Format a structured FitnessPlan object."""
        try:
            # Extract basic plan info
            plan_name = getattr(plan_obj, 'name', 'Fitness Plan')
            plan_goal = getattr(plan_obj, 'goal', '')
            plan_description = getattr(plan_obj, 'description', '')
            meal_plan = getattr(plan_obj, 'meal_plan', '')
            start_date = getattr(plan_obj, 'start_date', None)
            target_date = getattr(plan_obj, 'target_date', None)
            
            # Format header
            formatted = f"# 🏋️ {plan_name}\n\n"
            
            if plan_goal:
                formatted += f"**🎯 Goal:** {plan_goal}\n\n"
            
            if plan_description:
                formatted += f"**📋 Overview:** {plan_description}\n\n"
            
            # Add timeline information
            if start_date or target_date:
                formatted += "**📅 Timeline:**\n"
                if start_date:
                    formatted += f"- **Start Date:** {start_date.strftime('%B %d, %Y')}\n"
                if target_date:
                    formatted += f"- **Target Date:** {target_date.strftime('%B %d, %Y')}\n"
                formatted += "\n"
            
            # Format training plan
            training_plan = getattr(plan_obj, 'training_plan', None)
            if training_plan:
                formatted += "## 💪 Training Plan\n\n"
                formatted += UIComponents._format_training_plan(training_plan)
            
            # Format meal plan
            if meal_plan:
                formatted += "\n## 🥗 Meal Plan\n\n"
                formatted += f"{meal_plan}\n\n"
            
            # Add footer
            formatted += "## 📊 Additional Information\n\n"
            formatted += "- Plan created with AI assistance\n"
            formatted += "- Customize as needed for your preferences\n"
            formatted += "- Consult healthcare providers for medical advice\n\n"
            formatted += "---\n"
            formatted += "*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"
            
            return formatted
            
        except Exception as e:
            return f"**Error Formatting Plan Object**\n\n{str(e)}"

    @staticmethod
    def _format_training_plan(training_plan: Any) -> str:
        """Format a TrainingPlan object."""
        try:
            formatted = ""
            
            # Get training plan details
            plan_name = getattr(training_plan, 'name', 'Training Plan')
            plan_description = getattr(training_plan, 'description', '')
            
            formatted += f"**{plan_name}**\n\n"
            if plan_description:
                formatted += f"{plan_description}\n\n"
            
            # Check for the new structure with training_periods
            training_periods = getattr(training_plan, 'training_periods', None)
            if training_periods:
                formatted += UIComponents._format_training_periods(training_periods)
            else:
                # Fallback to legacy training_plan_splits structure
                training_splits = getattr(training_plan, 'training_plan_splits', [])
                if training_splits:
                    formatted += UIComponents._format_training_splits_with_dates(training_splits, None)
                else:
                    formatted += "No training periods defined.\n\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting training plan: {str(e)}"

    @staticmethod
    def _format_training_splits_with_dates(training_splits: list, target_event_date: Any = None) -> str:
        """Format training splits with calculated date ranges."""
        try:
            from datetime import date, timedelta
            
            formatted = ""
            current_date = date.today()
            
            # Sort splits by order
            sorted_splits = sorted(training_splits, key=lambda x: getattr(x, 'order', 0))
            
            for split in sorted_splits:
                # Get split details
                split_name = getattr(split, 'name', 'Training Split')
                phase_name = getattr(split, 'phase_name', split_name)
                phase_type = getattr(split, 'phase_type', None)
                duration_weeks = getattr(split, 'duration_weeks', 1)
                split_start_date = getattr(split, 'start_date', None)
                
                # Calculate start date for this split
                if split_start_date:
                    start_date = split_start_date
                else:
                    start_date = current_date
                
                # Calculate end date
                end_date = start_date + timedelta(weeks=duration_weeks) - timedelta(days=1)
                
                # Update current_date for next split
                current_date = end_date + timedelta(days=1)
                
                # Format phase type emoji
                phase_emojis = {
                    'base_building': '🏗️',
                    'strength': '💪',
                    'power': '⚡',
                    'peak': '🔥',
                    'taper': '📉',
                    'recovery': '😌',
                    'maintenance': '⚖️'
                }
                phase_type_str = str(phase_type).replace('PhaseType.', '').lower() if phase_type else 'training'
                phase_emoji = phase_emojis.get(phase_type_str, '📅')
                
                # Format the split header with date range
                formatted += f"### {phase_emoji} {phase_name}\n"
                formatted += f"**📅 Duration:** {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} ({duration_weeks} week{'s' if duration_weeks != 1 else ''})\n\n"
                
                # Add split description and training days
                formatted += UIComponents._format_training_split_content(split)
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting training splits with dates: {str(e)}"

    @staticmethod
    def _format_training_split(split: Any) -> str:
        """Format a TrainingPlanSplit object (legacy method, use _format_training_splits_with_dates for new formatting)."""
        try:
            formatted = ""
            
            # Get split details
            split_name = getattr(split, 'name', 'Training Split')
            split_description = getattr(split, 'description', '')
            
            formatted += f"### 📅 {split_name}\n\n"
            if split_description:
                formatted += f"{split_description}\n\n"
            
            # Format training days
            training_days = getattr(split, 'training_days', [])
            for day in training_days:
                formatted += UIComponents._format_training_day(day)
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting training split: {str(e)}"

    @staticmethod
    def _format_training_split_content(split: Any) -> str:
        """Format the content of a TrainingPlanSplit object (without header/dates)."""
        try:
            formatted = ""
            
            # Get split details
            split_description = getattr(split, 'description', '')
            
            if split_description:
                formatted += f"*{split_description}*\n\n"
            
            # Format training days
            training_days = getattr(split, 'training_days', [])
            for day in training_days:
                formatted += UIComponents._format_training_day(day)
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting training split content: {str(e)}"

    @staticmethod
    def _format_training_periods(training_periods: list) -> str:
        """Format training periods from the new Pydantic structure."""
        try:
            formatted = ""
            
            for period_idx, period in enumerate(training_periods, 1):
                # Format period header
                period_name = getattr(period, 'name', f'Training Period {period_idx}')
                period_description = getattr(period, 'description', '')
                period_intensity = getattr(period, 'intensity', None)
                start_date = getattr(period, 'start_date', None)
                
                formatted += f"### 📅 Phase {period_idx}: {period_name}\n\n"
                
                if period_description:
                    formatted += f"{period_description}\n\n"
                
                # Add period details
                period_details = []
                if start_date:
                    period_details.append(f"**Start Date:** {start_date.strftime('%B %d, %Y')}")
                if period_intensity:
                    intensity_emojis = {
                        'rest': '😴', 'light': '🟢', 'moderate': '🟡', 'heavy': '🔴', 'max_effort': '🔥'
                    }
                    intensity_str = str(period_intensity).lower()
                    intensity_emoji = intensity_emojis.get(intensity_str, '⚪')
                    period_details.append(f"**Overall Intensity:** {intensity_emoji} {intensity_str.title()}")
                
                if period_details:
                    formatted += f"{' | '.join(period_details)}\n\n"
                
                # Format the training split for this period
                training_split = getattr(period, 'training_split', None)
                if training_split:
                    formatted += UIComponents._format_new_training_split(training_split)
                
                formatted += "---\n\n"
            
            return formatted
            
        except Exception as e:
            return f"**Error Formatting Training Periods**\n\n{str(e)}"

    @staticmethod
    def _format_new_training_split(training_split: Any) -> str:
        """Format a TrainingSplit object from the new Pydantic structure."""
        try:
            formatted = ""
            
            # Get split details
            split_name = getattr(training_split, 'name', 'Training Split')
            split_description = getattr(training_split, 'description', '')
            
            formatted += f"**🗓️ {split_name}**\n\n"
            if split_description:
                formatted += f"{split_description}\n\n"
            
            # Format training days
            training_days = getattr(training_split, 'training_days', [])
            if training_days:
                # Sort by order_number if available
                sorted_days = sorted(training_days, key=lambda x: getattr(x, 'order_number', 0))
                for day in sorted_days:
                    formatted += UIComponents._format_training_day(day)
                    formatted += "\n"
            else:
                formatted += "No training days defined for this split.\n\n"
            
            return formatted
            
        except Exception as e:
            return f"**Error Formatting Training Split**\n\n{str(e)}"

    @staticmethod 
    def _format_training_day(day: Any) -> str:
        """Format a TrainingDay object."""
        try:
            formatted = ""
            
            # Get day details
            day_name = getattr(day, 'name', 'Training Day')
            day_description = getattr(day, 'description', '')
            day_order = getattr(day, 'order_number', '')
            day_intensity = getattr(day, 'intensity', None)
            exercises = getattr(day, 'exercises', [])
            
            # Determine if this is a rest day
            is_rest_day = (
                not exercises or 
                len(exercises) == 0 or 
                (day_intensity and str(day_intensity).lower() == 'rest') or
                day_name.lower().find('rest') != -1
            )
            
            # Format day header
            day_emoji = "😴" if is_rest_day else "💪"
            formatted += f"#### {day_emoji} Day {day_order}: {day_name}\n\n"
            
            if day_description:
                formatted += f"*{day_description}*\n\n"
            
            if day_intensity and not is_rest_day:
                intensity_emojis = {
                    'light': '🟢',
                    'moderate': '🟡', 
                    'heavy': '🔴',
                    'max_effort': '🔥',
                    'rest': '😴'
                }
                intensity_str = str(day_intensity).replace('IntensityLevel.', '').replace('<', '').replace('>', '').split(':')[0].lower()
                intensity_emoji = intensity_emojis.get(intensity_str, '⚪')
                formatted += f"**Intensity:** {intensity_emoji} {intensity_str.title()}\n\n"
            
            # Format exercises
            if not is_rest_day and exercises:
                formatted += "**Exercises:**\n\n"
                for i, exercise in enumerate(exercises, 1):
                    formatted += UIComponents._format_exercise(exercise, i)
                    formatted += "\n"
            elif is_rest_day:
                formatted += "**Rest Day** - Focus on recovery, light stretching, or gentle activities.\n\n"
            else:
                formatted += "**No exercises defined for this day.**\n\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting training day: {str(e)}"

    @staticmethod
    def _format_exercise(exercise: Any, number: int) -> str:
        """Format an Exercise object."""
        try:
            # Get exercise details
            name = getattr(exercise, 'name', 'Exercise')
            description = getattr(exercise, 'description', '')
            sets = getattr(exercise, 'sets', None)
            reps = getattr(exercise, 'reps', None)
            duration = getattr(exercise, 'duration', None)
            distance = getattr(exercise, 'distance', None)
            intensity = getattr(exercise, 'intensity', None)
            
            formatted = f"{number}. **{name}**\n"
            
            # Add sets/reps/duration/distance info
            workout_details = []
            if sets:
                workout_details.append(f"{sets} sets")
            if reps:
                workout_details.append(f"{reps} reps")
            if duration:
                if duration < 60:
                    workout_details.append(f"{duration}s")
                else:
                    minutes = duration // 60
                    seconds = duration % 60
                    if seconds > 0:
                        workout_details.append(f"{minutes}m {seconds}s")
                    else:
                        workout_details.append(f"{minutes}m")
            if distance:
                if distance >= 1000:
                    workout_details.append(f"{distance / 1000:.1f}km")
                else:
                    workout_details.append(f"{distance}m")
            
            if workout_details:
                formatted += f"   *{' × '.join(workout_details)}*"
                
            if intensity:
                intensity_emojis = {
                    'light': '🟢',
                    'moderate': '🟡',
                    'heavy': '🔴', 
                    'max_effort': '🔥',
                    'rest': '😴'
                }
                intensity_str = str(intensity).replace('IntensityLevel.', '').replace('<', '').replace('>', '').split(':')[0].lower()
                intensity_emoji = intensity_emojis.get(intensity_str, '⚪')
                formatted += f" - {intensity_emoji} {intensity_str.title()}"
            
            formatted += "\n"
            
            if description:
                formatted += f"   *{description}*\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting exercise: {str(e)}"

    @staticmethod
    def _format_structured_plan_string(plan_str: str) -> str:
        """Format a string representation of a structured fitness plan."""
        try:
            import re
            
            # Extract plan name
            name_match = re.search(r"🏋️\s*([^\n]*?)Training Plan", plan_str)
            if not name_match:
                name_match = re.search(r"name='([^']*)'", plan_str)
            plan_name = name_match.group(1).strip() if name_match else "Fitness Plan"
            
            # Extract meal plan section
            meal_match = re.search(r"🥗 Meal Plan\n(.*?)(?=📊|$)", plan_str, re.DOTALL)
            meal_plan = meal_match.group(1).strip() if meal_match else ""
            
            # Extract training plan section with structured data
            formatted = f"# 🏋️ {plan_name}\n\n"
            
            # Parse and format the structured training data
            training_match = re.search(r"training_plan_splits=\[(.*?)\]\]", plan_str, re.DOTALL)
            if training_match:
                formatted += "## 💪 Training Plan\n\n"
                formatted += UIComponents._parse_and_format_training_data(training_match.group(1))
            
            # Add meal plan
            if meal_plan:
                formatted += "\n## 🥗 Meal Plan\n\n"
                formatted += f"{meal_plan}\n\n"
            
            # Add footer
            formatted += "## 📊 Additional Information\n\n"
            formatted += "- Plan created with AI assistance\n"
            formatted += "- Customize as needed for your preferences\n"
            formatted += "- Consult healthcare providers for medical advice\n\n"
            formatted += "---\n"
            formatted += "*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"
            
            return formatted
            
        except Exception as e:
            return f"**Error Parsing Structured Plan**\n\n{str(e)}\n\nRaw content:\n{plan_str}"

    @staticmethod
    def _parse_and_format_training_data(training_data: str) -> str:
        """Parse and format the training data from string representation."""
        try:
            import re
            
            formatted = ""
            
            # Extract split information
            split_name_match = re.search(r"name='([^']*)'", training_data)
            split_name = split_name_match.group(1) if split_name_match else "Weekly Split"
            
            split_desc_match = re.search(r"description='([^']*)'", training_data)
            split_desc = split_desc_match.group(1) if split_desc_match else ""
            
            formatted += f"**{split_name}**\n\n"
            if split_desc:
                formatted += f"{split_desc}\n\n"
            
            # Extract training days
            days_pattern = r"TrainingDay\((.*?)\)(?=, TrainingDay\(|$)"
            days = re.findall(days_pattern, training_data, re.DOTALL)
            
            for day_data in days:
                formatted += UIComponents._parse_and_format_day_data(day_data)
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            return f"Error parsing training data: {str(e)}"

    @staticmethod
    def _parse_and_format_day_data(day_data: str) -> str:
        """Parse and format a single training day from string representation."""
        try:
            import re
            
            # Extract day details
            name_match = re.search(r"name='([^']*)'", day_data)
            day_name = name_match.group(1) if name_match else "Training Day"
            
            order_match = re.search(r"order_number=(\d+)", day_data)
            day_order = order_match.group(1) if order_match else "1"
            
            desc_match = re.search(r"description='([^']*)'", day_data)
            day_description = desc_match.group(1) if desc_match else ""
            
            rest_match = re.search(r"rest_day=(\w+)", day_data)
            is_rest_day = rest_match and rest_match.group(1) == "True"
            
            intensity_match = re.search(r"intensity=<IntensityLevel\.(\w+):", day_data)
            day_intensity = intensity_match.group(1) if intensity_match else None
            
            # Format day header
            day_emoji = "😴" if is_rest_day else "💪"
            formatted = f"#### {day_emoji} Day {day_order}: {day_name}\n\n"
            
            if day_description:
                formatted += f"*{day_description}*\n\n"
            
            if day_intensity and not is_rest_day:
                intensity_emojis = {
                    'LIGHT': '🟢',
                    'MODERATE': '🟡',
                    'HEAVY': '🔴',
                    'MAX_EFFORT': '🔥'
                }
                intensity_emoji = intensity_emojis.get(day_intensity, '⚪')
                formatted += f"**Intensity:** {intensity_emoji} {day_intensity.title()}\n\n"
            
            # Parse exercises if not rest day
            if not is_rest_day and 'exercises=[' in day_data:
                exercises_match = re.search(r"exercises=\[(.*?)\]", day_data, re.DOTALL)
                if exercises_match:
                    exercises_data = exercises_match.group(1)
                    formatted += "**Exercises:**\n\n"
                    formatted += UIComponents._parse_and_format_exercises(exercises_data)
            elif is_rest_day:
                formatted += "**Rest Day** - Focus on recovery, light stretching, or gentle activities.\n\n"
            
            return formatted
            
        except Exception as e:
            return f"Error parsing day data: {str(e)}"

    @staticmethod
    def _parse_and_format_exercises(exercises_data: str) -> str:
        """Parse and format exercises from string representation."""
        try:
            import re
            
            formatted = ""
            
            # Extract individual exercises
            exercise_pattern = r"Exercise\((.*?)\)(?=, Exercise\(|$)"
            exercises = re.findall(exercise_pattern, exercises_data, re.DOTALL)
            
            for i, exercise_data in enumerate(exercises, 1):
                # Extract exercise details
                name_match = re.search(r"name='([^']*)'", exercise_data)
                name = name_match.group(1) if name_match else "Exercise"
                
                desc_match = re.search(r"description='([^']*)'", exercise_data)
                description = desc_match.group(1) if desc_match else ""
                
                sets_match = re.search(r"sets=(\d+)", exercise_data)
                sets = sets_match.group(1) if sets_match else None
                
                reps_match = re.search(r"reps=(\d+)", exercise_data)
                reps = reps_match.group(1) if reps_match else None
                
                duration_match = re.search(r"duration=(\d+)", exercise_data)
                duration = duration_match.group(1) if duration_match else None
                
                intensity_match = re.search(r"intensity=<IntensityLevel\.(\w+):", exercise_data)
                intensity = intensity_match.group(1) if intensity_match else None
                
                # Format exercise
                formatted += f"{i}. **{name}**\n"
                
                # Add workout details
                workout_details = []
                if sets:
                    workout_details.append(f"{sets} sets")
                if reps:
                    workout_details.append(f"{reps} reps")
                if duration:
                    workout_details.append(f"{duration}s")
                
                if workout_details:
                    formatted += f"   *{' × '.join(workout_details)}*"
                
                if intensity:
                    intensity_emojis = {
                        'LIGHT': '🟢',
                        'MODERATE': '🟡',
                        'HEAVY': '🔴',
                        'MAX_EFFORT': '🔥'
                    }
                    intensity_emoji = intensity_emojis.get(intensity, '⚪')
                    formatted += f" - {intensity_emoji} {intensity.title()}"
                
                formatted += "\n"
                
                if description:
                    formatted += f"   *{description}*\n"
                
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            return f"Error parsing exercises: {str(e)}"
