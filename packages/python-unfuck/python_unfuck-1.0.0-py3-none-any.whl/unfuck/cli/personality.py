"""
Personality system for unfuck.
Makes debugging fun with encouraging messages and humor!
"""

import random
from typing import List, Dict, Any
from enum import Enum


class PersonalityMode(Enum):
    """Different personality modes for unfuck."""
    ENCOURAGING = "encouraging"
    SARCASTIC = "sarcastic"
    ZEN = "zen"
    PROFESSIONAL = "professional"
    MEME = "meme"


class UnfuckPersonality:
    """Personality system for unfuck messages."""
    
    def __init__(self, mode: PersonalityMode = PersonalityMode.ENCOURAGING):
        self.mode = mode
        self.streak_count = 0
        self.total_fixes = 0
        
        # Message templates
        self.messages = {
            PersonalityMode.ENCOURAGING: {
                "start": [
                    "🔥 I got you! Let me fix that error...",
                    "✨ Don't worry, I've seen this before!",
                    "🚀 Time to unfuck this code!",
                    "💪 I'm on it! Analyzing the problem...",
                    "🎯 Got it! Let me work my magic...",
                ],
                "success": [
                    "🎉 Unfucked! Your code is running!",
                    "✨ Success! That error is history!",
                    "🚀 Boom! Fixed and ready to go!",
                    "💯 Perfect! Your code is back on track!",
                    "🎊 Unfucked successfully! You're welcome!",
                ],
                "failure": [
                    "😅 Hmm, that was trickier than expected...",
                    "🤔 Let me try a different approach...",
                    "💭 This one needs more thinking...",
                    "🔍 Interesting error, let me dig deeper...",
                ],
                "streak": [
                    "🔥 You're on fire! {count} fixes in a row!",
                    "⚡ Unfuck streak: {count}! Keep it up!",
                    "🎯 {count} errors down! You're unstoppable!",
                    "💪 {count} fixes! You're becoming an unfuck master!",
                ]
            },
            
            PersonalityMode.SARCASTIC: {
                "start": [
                    "🙄 Oh great, another error...",
                    "😒 This again? *sigh* fixing...",
                    "🤦‍♂️ Really? Let me fix this for you...",
                    "😤 Fine, I'll unfuck this mess...",
                    "🤷‍♂️ Another day, another error to fix...",
                ],
                "success": [
                    "😏 There, fixed it. You're welcome.",
                    "🙃 Unfucked. Try not to break it again.",
                    "😎 Boom! Fixed. I'm basically a genius.",
                    "🤨 There you go. Don't mess it up this time.",
                    "😌 Unfucked. I should charge for this.",
                ],
                "failure": [
                    "🤔 Hmm, this one's actually challenging...",
                    "😬 Okay, this error is being stubborn...",
                    "🤯 Whoa, this is a weird one...",
                    "😵 This error is giving me a headache...",
                ],
                "streak": [
                    "😏 {count} fixes in a row. Not bad, human.",
                    "🤨 {count} errors? You're really trying to break things.",
                    "😎 {count} unfucks! I'm basically your debugging hero.",
                    "🙄 {count} fixes. Maybe you should learn to code better?",
                ]
            },
            
            PersonalityMode.ZEN: {
                "start": [
                    "🧘‍♂️ Breathe... let me find the balance in your code...",
                    "🌸 The error is temporary, the fix is eternal...",
                    "🕯️ In the silence of debugging, wisdom emerges...",
                    "🌿 Let me bring harmony to your code...",
                    "☯️ The error and the fix are one...",
                ],
                "success": [
                    "🌅 The code flows like water now...",
                    "🌸 Harmony restored. Your code is at peace.",
                    "🕊️ The error has been transcended...",
                    "🌿 Balance achieved. Your code breathes freely.",
                    "☯️ Perfect equilibrium restored.",
                ],
                "failure": [
                    "🌊 The error flows deeper than expected...",
                    "🌙 Sometimes the path is not yet clear...",
                    "🌿 The code needs more time to reveal its truth...",
                    "🕯️ Patience, young coder. The answer will come...",
                ],
                "streak": [
                    "🌅 {count} errors transcended. You walk the path of wisdom.",
                    "🌸 {count} fixes. Your code finds its rhythm.",
                    "🕊️ {count} unfucks. You are becoming one with the code.",
                    "🌿 {count} errors resolved. The universe smiles upon you.",
                ]
            },
            
            PersonalityMode.PROFESSIONAL: {
                "start": [
                    "🔧 Analyzing error and preparing fix...",
                    "⚙️ Error detected. Initiating repair sequence...",
                    "🛠️ Processing error data and generating solution...",
                    "🔍 Error analysis in progress...",
                    "⚡ Executing automated fix protocol...",
                ],
                "success": [
                    "✅ Error resolved successfully.",
                    "🎯 Fix applied. System operational.",
                    "⚡ Repair complete. Code execution restored.",
                    "🔧 Error eliminated. Functionality verified.",
                    "✅ Fix successful. No further action required.",
                ],
                "failure": [
                    "⚠️ Error resolution requires additional analysis.",
                    "🔍 Complex error detected. Escalating to advanced protocols.",
                    "⚙️ Standard fix protocols insufficient. Analyzing alternatives.",
                    "🛠️ Error pattern not recognized. Manual intervention may be required.",
                ],
                "streak": [
                    "📊 Performance metric: {count} consecutive fixes achieved.",
                    "🎯 Efficiency rating: {count} errors resolved in sequence.",
                    "⚡ System reliability: {count} successful interventions.",
                    "🔧 Maintenance log: {count} automated repairs completed.",
                ]
            },
            
            PersonalityMode.MEME: {
                "start": [
                    "🚀 TO THE MOON! (with your fixed code)",
                    "💎 DIAMOND HANDS! (holding your working script)",
                    "🔥 THIS IS THE WAY! (to fix errors)",
                    "🚀 HODL! (your code until it works)",
                    "💪 STONKS! (your debugging skills)",
                ],
                "success": [
                    "🚀 TO THE MOON! Your code is working!",
                    "💎 DIAMOND HANDS! You held through the error!",
                    "🔥 THIS IS THE WAY! Error fixed!",
                    "🚀 HODL! Your code is now unstoppable!",
                    "💪 STONKS! Your debugging game is strong!",
                ],
                "failure": [
                    "📉 Paper hands! This error is tough...",
                    "🐻 Bear market for your code right now...",
                    "💸 FUD! This error is spreading fear...",
                    "📊 Market correction needed for this code...",
                ],
                "streak": [
                    "🚀 {count} fixes! You're going TO THE MOON!",
                    "💎 {count} DIAMOND HANDS! Keep holding!",
                    "🔥 {count} THIS IS THE WAY! You're unstoppable!",
                    "💪 {count} STONKS! Your portfolio is looking good!",
                ]
            }
        }
    
    def get_start_message(self) -> str:
        """Get a start message for fixing."""
        messages = self.messages[self.mode]["start"]
        return random.choice(messages)
    
    def get_success_message(self) -> str:
        """Get a success message."""
        self.total_fixes += 1
        self.streak_count += 1
        
        messages = self.messages[self.mode]["success"]
        base_message = random.choice(messages)
        
        # Add streak message if on a streak
        if self.streak_count > 1:
            streak_messages = self.messages[self.mode]["streak"]
            streak_message = random.choice(streak_messages).format(count=self.streak_count)
            return f"{base_message}\n{streak_message}"
        
        return base_message
    
    def get_failure_message(self) -> str:
        """Get a failure message."""
        self.streak_count = 0  # Reset streak on failure
        messages = self.messages[self.mode]["failure"]
        return random.choice(messages)
    
    def get_celebration_message(self) -> str:
        """Get a special celebration message."""
        celebrations = {
            1: "🎉 First unfuck! Welcome to the club!",
            10: "🔥 10 unfucks! You're getting the hang of this!",
            50: "💎 50 unfucks! You're a debugging diamond!",
            100: "🚀 100 unfucks! You're an unfuck master!",
            500: "👑 500 unfucks! You're the unfuck king/queen!",
            1000: "🏆 1000 unfucks! You're a legend!",
        }
        
        return celebrations.get(self.total_fixes, "")
    
    def get_achievement_message(self) -> str:
        """Get achievement messages."""
        achievements = {
            5: "🏅 Achievement Unlocked: Unfuck Novice!",
            25: "🥉 Achievement Unlocked: Unfuck Bronze!",
            50: "🥈 Achievement Unlocked: Unfuck Silver!",
            100: "🥇 Achievement Unlocked: Unfuck Gold!",
            250: "💎 Achievement Unlocked: Unfuck Diamond!",
            500: "👑 Achievement Unlocked: Unfuck Royalty!",
        }
        
        return achievements.get(self.total_fixes, "")
    
    def get_ascii_art(self) -> str:
        """Get ASCII art for celebrations."""
        arts = [
            """
    🔥 UNFUCKED! 🔥
    ╔═══════════════╗
    ║  Your code is  ║
    ║   working!     ║
    ╚═══════════════╝
            """,
            """
    ✨ SUCCESS! ✨
    ╭─────────────╮
    │  Error: 0   │
    │  Fixes: 1   │
    │  You: Win!  │
    ╰─────────────╯
            """,
            """
    🚀 TO THE MOON! 🚀
    ╔═══════════════╗
    ║  Code fixed!  ║
    ║  Stonks up!   ║
    ╚═══════════════╝
            """,
        ]
        
        return random.choice(arts)
    
    def set_mode(self, mode: PersonalityMode):
        """Change personality mode."""
        self.mode = mode
    
    def get_stats(self) -> Dict[str, Any]:
        """Get personality statistics."""
        return {
            "mode": self.mode.value,
            "total_fixes": self.total_fixes,
            "current_streak": self.streak_count,
            "achievements": self.get_achievement_message(),
            "celebration": self.get_celebration_message()
        }
    
    def reset_streak(self):
        """Reset the current streak."""
        self.streak_count = 0
    
    def get_encouragement(self) -> str:
        """Get random encouragement."""
        encouragements = [
            "You've got this! 💪",
            "Every error is a learning opportunity! 📚",
            "You're becoming a better programmer! 🚀",
            "Debugging is an art, and you're the artist! 🎨",
            "Keep going! You're doing great! ⭐",
            "Every fix makes you stronger! 💪",
            "You're solving problems like a pro! 🎯",
            "Don't give up! The solution is out there! 🔍",
        ]
        
        return random.choice(encouragements)
