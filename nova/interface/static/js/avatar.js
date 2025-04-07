import { VRMLoader } from '@pixiv/three-vrm';

// avatar.js - Gestión del avatar 3D para Nova


document.addEventListener('DOMContentLoaded', function() {
    // Contenedor del avatar
    const avatarContainer = document.getElementById('avatar-container');
    
    // Variables para Three.js
    let scene, camera, renderer, model;
    let mixer, clock;
    let currentAnimation = null;
    
    // Inicializar la escena 3D
    function initScene() {
        // Crear escena
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf0f0f0);
        
        // Crear cámara
        camera = new THREE.PerspectiveCamera(
            45,
            avatarContainer.clientWidth / avatarContainer.clientHeight,
            0.1,
            1000
        );
        camera.position.set(0, 1, 5);
        camera.lookAt(0, 1, 0);
        
        // Crear renderer
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(avatarContainer.clientWidth, avatarContainer.clientHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.outputEncoding = THREE.sRGBEncoding;
        avatarContainer.appendChild(renderer.domElement);
        
        // Iluminación
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, 10, 10);
        scene.add(directionalLight);
        
        // Inicializar reloj para animaciones
        clock = new THREE.Clock();
        
        // Cargar modelo (placeholder - se debe reemplazar con el modelo real)
        loadModel();
        
        // Manejar redimensionamiento de ventana
        window.addEventListener('resize', onWindowResize);
        
        // Iniciar bucle de renderizado
        animate();
    }
    
    // Cargar modelo 3D
    function loadModel() {
        const loader = new VRMLoader();
        loader.load('/Users/oriol/dev/interface AI/nova/interface/static/models/model.vrm', function(vrm) {
            model = vrm.scene;
            scene.add(model);
            mixer = new THREE.AnimationMixer(model);
            // Configurar animaciones naturales
            const breatheAnimation = mixer.clipAction(vrm.animations.find(clip => clip.name === 'Breathe'));
            breatheAnimation.play();
            breatheAnimation.setLoop(THREE.LoopRepeat);
            breatheAnimation.setEffectiveTimeScale(0.5);

            const idleAnimation = mixer.clipAction(vrm.animations.find(clip => clip.name === 'Idle'));
            idleAnimation.play();
            idleAnimation.setLoop(THREE.LoopRepeat);
            idleAnimation.setEffectiveTimeScale(0.5);

            const blinkAnimation = mixer.clipAction(vrm.animations.find(clip => clip.name === 'Blink'));
            blinkAnimation.play();
            blinkAnimation.setLoop(THREE.LoopRepeat);
            blinkAnimation.setEffectiveTimeScale(0.5);
        });
    }
    
    // Manejar redimensionamiento de ventana
    function onWindowResize() {
        camera.aspect = avatarContainer.clientWidth / avatarContainer.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(avatarContainer.clientWidth, avatarContainer.clientHeight);
    }
    
    // Bucle de animación
    function animate() {
        requestAnimationFrame(animate);
        
        // Actualizar animaciones
        if (mixer) {
            mixer.update(clock.getDelta());
        }
        
        // Rotar el modelo placeholder
        // if (model) {
        // model.rotation.y += 0.01;
        // }
        
        renderer.render(scene, camera);
    }
    
    // Iniciar la escena
    initScene();
});