from flask import Blueprint, render_template, jsonify, request
from app.models.models import Disease

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@main_bp.route('/api/diseases')
def list_diseases():
    diseases = Disease.query.all()
    return jsonify({'success': True, 'data': [{'id': d.id, 'name': d.name, 'crop_type': d.crop_type} for d in diseases]})

@main_bp.route('/api/disease/<int:did>')
def get_disease(did):
    d = Disease.query.get_or_404(did)
    return jsonify({
        'id': d.id, 'name': d.name, 'crop_type': d.crop_type,
        'symptoms': d.symptoms, 'causes': d.causes,
        'organic_treatment': d.organic_treatment,
        'chemical_treatment': d.chemical_treatment,
        'preventive_measures': d.preventive_measures
    })

@main_bp.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'response': 'Please provide a message.'}), 400
        
        query = data.get('message', '').lower().strip()
        if not query:
            return jsonify({'success': False, 'response': 'Please ask a question.'}), 400
        
        response = generate_intelligent_response(query)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({'success': False, 'response': 'Sorry, something went wrong. Please try again.'}), 500


def generate_intelligent_response(query):
    """Intelligent context-aware chatbot for farming questions"""
    
    # Greetings
    if any(word in query for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm your CropGuard AI assistant. I can help with crop diseases, treatments, symptoms, and farming advice. What would you like to know?"
    
    # Help/capabilities
    if any(word in query for word in ['help', 'can you', 'what can', 'how to use']):
        return "I can help you with:\n• Identifying crop diseases by symptoms\n• Treatment recommendations (organic & chemical)\n• Preventive measures\n• Fertilizer and nutrient advice\n• General farming best practices\n\nJust ask me anything about crop health!"
    
    # Disease-specific queries
    diseases = Disease.query.all()
    
    # Search for specific disease mentions
    for disease in diseases:
        if disease.name.lower() in query or disease.crop_type.lower() in query:
            # Symptoms query
            if any(word in query for word in ['symptom', 'sign', 'look like', 'identify', 'how to know']):
                return f"**{disease.name}** symptoms:\n{disease.symptoms}\n\nCauses: {disease.causes}"
            
            # Treatment query
            if any(word in query for word in ['treat', 'cure', 'remedy', 'fix', 'control', 'manage']):
                if 'organic' in query or 'natural' in query:
                    return f"**Organic treatment for {disease.name}:**\n{disease.organic_treatment}"
                elif 'chemical' in query or 'pesticide' in query or 'fungicide' in query:
                    return f"**Chemical treatment for {disease.name}:**\n{disease.chemical_treatment}"
                else:
                    return f"**Treatment for {disease.name}:**\n\n🌿 Organic: {disease.organic_treatment}\n\n🧪 Chemical: {disease.chemical_treatment}"
            
            # Prevention query
            if any(word in query for word in ['prevent', 'avoid', 'stop', 'protect']):
                return f"**Prevention for {disease.name}:**\n{disease.preventive_measures}"
            
            # General info
            return f"**{disease.name}** ({disease.crop_type})\n\n🔍 Symptoms: {disease.symptoms}\n\n💊 Treatment: {disease.organic_treatment}\n\n🛡️ Prevention: {disease.preventive_measures}"
    
    # General symptom description
    if any(word in query for word in ['spot', 'yellow', 'brown', 'wilting', 'rot', 'mold', 'lesion']):
        matching = []
        for d in diseases:
            if any(word in d.symptoms.lower() for word in query.split()):
                matching.append(d)
        if matching:
            result = "Based on symptoms, possible diseases:\n"
            for d in matching[:3]:
                result += f"\n• **{d.name}** ({d.crop_type}): {d.symptoms[:100]}..."
            return result + "\n\nUpload an image for accurate detection!"
        return "Could you describe the symptoms more specifically? (e.g., leaf spots, discoloration, wilting)"
    
    # Fertilizer/nutrient questions
    if any(word in query for word in ['fertilizer', 'nutrient', 'npk', 'nitrogen', 'phosphorus', 'potassium', 'compost']):
        return "**Fertilizer recommendations:**\n• NPK 20-20-20 for balanced growth\n• High nitrogen (urea) for leafy crops\n• High phosphorus for flowering/fruiting\n• Potassium for disease resistance\n• Organic: Compost, manure, bone meal\n\nApply based on soil test results for best outcomes."
    
    # Irrigation/watering
    if any(word in query for word in ['water', 'irrigation', 'drip', 'sprinkler']):
        return "**Irrigation best practices:**\n• Water early morning or evening\n• Drip irrigation reduces disease risk\n• Avoid overhead watering for disease-prone crops\n• Monitor soil moisture regularly\n• Adjust frequency based on crop stage and weather"
    
    # Pest questions
    if any(word in query for word in ['pest', 'insect', 'bug', 'aphid', 'caterpillar']):
        return "**Pest management:**\n• Regular scouting and early detection\n• Biological control (beneficial insects)\n• Organic: Neem oil, insecticidal soaps\n• Chemical: Use IPM-approved pesticides\n• Crop rotation to break pest cycles\n\nFor specific pests, please describe them in detail."
    
    # Crop rotation
    if any(word in query for word in ['rotation', 'alternate', 'crop cycle']):
        return "**Crop rotation benefits:**\n• Breaks disease and pest cycles\n• Improves soil health\n• Reduces chemical dependency\n• Example: Legumes → Cereals → Root crops\n• Minimum 2-3 year rotation recommended"
    
    # Weather/climate
    if any(word in query for word in ['weather', 'rain', 'temperature', 'climate', 'season']):
        return "**Weather and crop health:**\n• High humidity favors fungal diseases\n• Excessive rain causes root rot\n• Heat stress reduces yields\n• Monitor weather forecasts for spray timing\n• Adjust irrigation based on rainfall"
    
    # Soil health
    if any(word in query for word in ['soil', 'ph', 'drainage', 'sandy', 'clay']):
        return "**Soil health tips:**\n• Test soil pH (most crops prefer 6.0-7.0)\n• Improve drainage with organic matter\n• Add compost for soil structure\n• Avoid over-tilling to preserve microbes\n• Use cover crops for soil enrichment"
    
    # Thanks
    if any(word in query for word in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! Feel free to ask if you need more help with your crops. Happy farming! 🌱"
    
    # Default for unrecognized queries
    return f"I understand you're asking about: '{query}'\n\nI can help with:\n• Disease identification and treatment\n• Crop-specific advice\n• Fertilizers and nutrients\n• Pest management\n• Irrigation and soil health\n\nCould you rephrase your question or ask about a specific crop disease?"
