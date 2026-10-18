# 3D Avatar Setup Guide for HERwell AI

## Quick Setup

### 1. Avatar Model Required

TheTalkingAvatar library requires a `.glb` (GLB) 3D model file. Replace the placeholder at:
```
frontend/public/avatar.glb
```

### 2. Where to Get 3D Avatars

#### Option A: InterviewFlow AI (Recommended)
1. Go to https://interviewflow.ai
2. Sign up for an account
3. Download avatar from your dashboard
4. Place in `frontend/public/avatar.glb`

#### Option B: Ready Player Me (Free)
1. Visit https://readyplayer.me
2. Create and customize your avatar
3. Download as `.glb` format
4. Place in `frontend/public/avatar.glb`

#### Option C: Mixamo (Free)
1. Visit https://www.mixamo.com
2. Select an avatar
3. Download in `.fbx` format
4. Convert to `.glb` using Blender or online converter
5. Place in `frontend/public/avatar.glb`

#### Option D: Sketchfab (Some Free)
1. Visit https://sketchfab.com
2. Search for "woman avatar" or "female character"
3. Filter by "Downloadable" and "Free"
4. Download in `.glb` format
5. Check license (ensure commercial use is allowed)
6. Place in `frontend/public/avatar.glb`

### 3. Avatar Specifications

**Recommended:**
- Format: `.glb` (preferred) or `.gltf`
- Poly count: < 50,000 polygons
- File size: < 10MB
- Includes: Facial blend shapes for lip-sync
- Style: Professional, diverse, representative

**For HERwell:**
- Female avatar (primary audience: women students)
- Professional appearance
- Clear facial features
- Suitable for wellness/mental health context
- Non-stereotypical representation

### 4. File Structure

Ensure your file structure looks like this:
```
frontend/
├── public/
│   ├── avatar.glb          # YOUR 3D MODEL (replace placeholder)
│   └── sdk/
│       └── viseme-model.bin # Already copied by setup script
└── src/
    └── components/
        └── HerwellVoiceAssistant.jsx
```

### 5. Testing the Avatar

After placing your `.glb` file:

```bash
cd frontend
npm run dev
```

Navigate to the voice assistant page and test:
1. Avatar should load and display
2. Test with text input
3. Test with voice input
4. Verify lip-sync animation

### 6. Troubleshooting

**Avatar doesn't load:**
- Check file is in `frontend/public/avatar.glb`
- Verify file format is `.glb`
- Check browser console for errors
- Ensure file size < 10MB

**Lip-sync not working:**
- Avatar must include facial blend shapes
- Check `viseme-model.bin` is in `public/sdk/`
- Verify audio is playing
- Check browser supports Web Audio API

**Performance issues:**
- Reduce poly count of avatar
- Compress texture files
- Use simpler lighting
- Consider LOD (Level of Detail) system

### 7. Alternative: Fallback to Basic Avatar

If 3D avatar doesn't work, the code has fallback support. The basic Three.js avatar can be restored by:
1. Reinstalling Three.js packages
2. Reverting to the old HerwellVoiceAssistant.jsx code

### 8. Production Deployment

For Render deployment:
1. Commit your `.glb` file to Git
2. Ensure file is in `frontend/public/`
3. File will be served automatically
4. No additional configuration needed

### 9. Legal Considerations

- Ensure you have rights to use the avatar
- Check commercial license if using from Sketchfab
- Attribute sources if required by license
- Consider creating custom avatar for production

---

## Example Avatar Sources

**Free Options:**
- Ready Player Me: https://readyplayer.me
- Mixamo: https://www.mixamo.com
- Sketchfab (Free section): https://sketchfab.com/search?downloadable=true&type=models

**Paid Options:**
- InterviewFlow AI: https://interviewflow.ai
- Adobe Mixamo: https://www.mixamo.com
- TurboSquid: https://www.turbosquid.com

**Custom Creation:**
- Blender (free): https://www.blender.org
- Maya (paid): https://www.autodesk.com/products/maya
- Cinema 4D (paid): https://www.maxon.net

---

## Current Status

✅ Package installed: `@interviewflowai/talking-avatar`
✅ Model file copied: `viseme-model.bin`
✅ Component updated: `HerwellVoiceAssistant.jsx`
✅ Placeholder created: `avatar.glb`
⚠️ **NEXT STEP:** Replace `avatar.glb` with your actual 3D model

---

**Repository:** https://github.com/Medazizzormati/HerWell
**Last Updated:** 2026-10-18
