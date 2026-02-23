import os
import json
import tempfile
from pathlib import Path
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import yt_dlp
import whisper
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
except ImportError:
    genai = None

from .models import Quiz, Question, Answer
from .serializers import QuizSerializer, QuizCreateSerializer, QuizUpdateSerializer


class QuizListCreateView(APIView):
    """
    API endpoint to manage quizzes.
    
    GET /api/quizzes/ - Get all quizzes for the authenticated user
    POST /api/quizzes/ - Create a new quiz from a YouTube video URL
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get all quizzes for the authenticated user.
        """
        try:
            quizzes = Quiz.objects.filter(user=request.user).prefetch_related('questions__answers')
            serializer = QuizSerializer(quizzes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """
        Create a new quiz from a YouTube video URL.
        
        Request: {"url": "https://www.youtube.com/watch?v=example"}
        Returns: Quiz object with all questions and answers
        """
        try:
            serializer = QuizCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            youtube_url = serializer.validated_data['url']
            
            video_info = self._extract_video_info(youtube_url)
            
            quiz = Quiz.objects.create(
                user=request.user,
                title=video_info['title'],
                description=video_info.get('description', '')[:500],
                youtube_url=youtube_url,
                transcript=video_info.get('transcript', '')
            )
            
            questions_data = self._generate_questions(video_info)
            
            # Create Question and Answer objects
            for idx, q_data in enumerate(questions_data):
                question = Question.objects.create(
                    quiz=quiz,
                    question_text=q_data['question'],
                    question_type='multiple_choice',
                    order=idx
                )
                
                # Create answer options
                for ans_idx, answer_text in enumerate(q_data['options']):
                    is_correct = (answer_text == q_data['correct_answer'])
                    Answer.objects.create(
                        question=question,
                        answer_text=answer_text,
                        is_correct=is_correct,
                        order=ans_idx
                    )
            
            serializer = QuizSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _extract_video_info(self, youtube_url):
        """
        Extract video information from YouTube URL using yt-dlp.
        Downloads audio and returns video metadata with transcript.
        Raises exception on failure.
        """
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp()
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading audio from {youtube_url}...")
                info = ydl.extract_info(youtube_url, download=True)
                
                audio_file = None
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp3'):
                        audio_file = os.path.join(temp_dir, file)
                        break
                
                if not audio_file:
                    raise RuntimeError("Failed to download or convert audio file from YouTube.")
                
                print(f"Transcribing audio: {audio_file}...")
                transcript = self._transcribe_audio(audio_file)
                
                return {
                    'title': info.get('title', 'Untitled Video'),
                    'description': info.get('description', '')[:500],
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'transcript': transcript,
                }
        finally:
            # Cleanup temp files
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
    
    def _transcribe_audio(self, audio_file):
        """
        Transcribe audio file using Whisper AI.
        Raises exception on failure.
        """
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("Transcribing audio...")
        result = model.transcribe(audio_file, language="de")
        transcript = result.get('text', '')
        
        if not transcript:
            raise ValueError("Whisper transcription returned empty result.")
        
        print(f"✅ Transcription completed: {len(transcript)} characters")
        return transcript
    
    def _generate_questions(self, video_info):
        """
        Generate quiz questions using Google Gemini Flash AI.
        Raises exception if AI is unavailable or fails - no fallback.
        """
        if genai is None:
            raise RuntimeError("Google Gemini module (google-genai) not installed or not available.")
        
        client = genai.Client()
        
        transcript = video_info.get('transcript', '')
        if not transcript:
            raise ValueError("No transcript available from video.")
        
        prompt = f"""
Basierend auf folgendem Transkript eines Videos, erstelle 10 Multiple-Choice Quizfragen.

Video Titel: {video_info.get('title', 'Untitled')}
Video Beschreibung: {video_info.get('description', '')}

Transkript:
{transcript[:3000]}

Bitte erstelle 10 Quizfragen im JSON-Format mit folgendem Schema:
[
  {{
    "question": "Die Frage?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A"
  }}
]

Wichtig:
- Alle Fragen müssen auf dem Transkript basieren
- Genau 4 Optionen pro Frage
- Die Optionen sollten plausibel sein
- Nur JSON zurückgeben, nichts anderes
"""
        
        print("Generating questions with Gemini...")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Parse JSON response
        # Try to extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        try:
            questions = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Gemini returned invalid JSON: {str(e)}. Response: {response_text[:200]}")
        
        if not questions or len(questions) == 0:
            raise ValueError("Gemini returned empty questions list.")
        
        print(f"✅ Generated {len(questions)} questions with Gemini")
        return questions

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    """
    Legacy endpoint wrapper for creating quiz.
    Can be used as an alternative to the class-based view.
    """
    view = QuizListCreateView.as_view()
    return view(request)


class QuizDetailView(APIView):
    """    
    GET /api/quizzes/{id}/ - Get a specific quiz with all questions
    PATCH /api/quizzes/{id}/ - Update specific fields of a quiz
    DELETE /api/quizzes/{id}/ - Delete a quiz permanently
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, quiz_id):
        """
        Get a specific quiz for the authenticated user.
        """
        try:
            try:
                quiz = Quiz.objects.prefetch_related('questions__answers').get(id=quiz_id)
            except Quiz.DoesNotExist:
                return Response(
                    {"error": "Quiz not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if quiz.user != request.user:
                return Response(
                    {"error": "Access denied. This quiz belongs to another user."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = QuizSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, quiz_id):
        """
        Partially update a quiz (title, description only).
        """
        try:
            try:
                quiz = Quiz.objects.prefetch_related('questions__answers').get(id=quiz_id)
            except Quiz.DoesNotExist:
                return Response(
                    {"error": "Quiz not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if quiz.user != request.user:
                return Response(
                    {"error": "Access denied. This quiz belongs to another user."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = QuizUpdateSerializer(quiz, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            
            response_serializer = QuizSerializer(quiz)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, quiz_id):
        """
        Delete a quiz and all associated questions permanently.
        """
        try:
            try:
                quiz = Quiz.objects.get(id=quiz_id)
            except Quiz.DoesNotExist:
                return Response(
                    {"error": "Quiz not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if quiz.user != request.user:
                return Response(
                    {"error": "Access denied. This quiz belongs to another user."},
                    status=status.HTTP_403_FORBIDDEN
                )
            quiz.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


