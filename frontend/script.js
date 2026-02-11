// Theme Toggle Functionality
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = themeToggle.querySelector('i');

// Check for saved theme or prefer-color-scheme
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
const currentTheme = localStorage.getItem('theme');

// Set initial theme
if (currentTheme === 'dark' || (!currentTheme && prefersDarkScheme.matches)) {
    document.body.classList.add('dark-theme');
    themeIcon.classList.remove('fa-moon');
    themeIcon.classList.add('fa-sun');
}

// Toggle theme function
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    
    if (document.body.classList.contains('dark-theme')) {
        localStorage.setItem('theme', 'dark');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    } else {
        localStorage.setItem('theme', 'light');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
    }
    
    // Update 3D visualization colors if needed
    updateVisualizationColors();
    createBackgroundAnimation();
}

themeToggle.addEventListener('click', toggleTheme);

// Update visualization colors based on theme
function updateVisualizationColors() {
    // This would update colors in the 3D visualizations
    // You might need to adjust the 3D materials based on the theme
    if (scene && scene.userData && scene.userData.nodes) {
        const isDark = document.body.classList.contains('dark-theme');
        
        scene.userData.nodes.forEach((node, i) => {
            const colors = isDark ? 
                [0x22d3ee, 0x3b82f6, 0x8b5cf6] : // Dark theme colors
                [0x06b6d4, 0x3b82f6, 0x8b5cf6]; // Light theme colors
            
            node.material.color.setHex(colors[i % 3]);
        });
    }
}

// Initialize ScrollReveal
ScrollReveal().reveal('.feature-card, .section-title, .section-subtitle', {
    delay: 200,
    distance: '30px',
    origin: 'bottom',
    opacity: 0,
    easing: 'cubic-bezier(0.5, 0, 0, 1)',
    interval: 100
});

// Background Animation
function createBackgroundAnimation() {
    const container = document.getElementById('background-animation');
    const isDark = document.body.classList.contains('dark-theme');
    
    const colors = isDark ? [
        'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(34, 211, 238, 0.05) 100%)',
        'linear-gradient(135deg, rgba(15, 23, 42, 0.03) 0%, rgba(59, 130, 246, 0.03) 100%)'
    ] : [
        'linear-gradient(135deg, rgba(37, 99, 235, 0.03) 0%, rgba(6, 182, 212, 0.03) 100%)',
        'linear-gradient(135deg, rgba(15, 23, 42, 0.02) 0%, rgba(37, 99, 235, 0.02) 100%)'
    ];
    
    // Clear existing shapes
    container.innerHTML = '';
    
    for (let i = 0; i < 8; i++) {
        const shape = document.createElement('div');
        shape.classList.add('floating-shape');
        
        // Random properties
        const size = Math.random() * 300 + 100;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const left = Math.random() * 100;
        const top = Math.random() * 100;
        const animationDuration = Math.random() * 25 + 15;
        const animationDelay = Math.random() * 5;
        
        shape.style.width = `${size}px`;
        shape.style.height = `${size}px`;
        shape.style.background = color;
        shape.style.left = `${left}%`;
        shape.style.top = `${top}%`;
        shape.style.animationDuration = `${animationDuration}s`;
        shape.style.animationDelay = `${animationDelay}s`;
        
        container.appendChild(shape);
    }
}

// Professional 3D Animation for Hero Section
let scene, camera, renderer;

function init3DAnimation() {
    // Create scene
    scene = new THREE.Scene();
    scene.background = null;
    
    // Create camera
    const container = document.getElementById('canvas-container');
    camera = new THREE.PerspectiveCamera(60, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    camera.position.z = 15;
    camera.position.y = 5;
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    
    // Create a floating network of nodes
    createNetwork();
    
    // Add subtle lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7);
    scene.add(directionalLight);
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start animation
    animate();
}

function createNetwork() {
    const isDark = document.body.classList.contains('dark-theme');
    
    // Create a central node
    const centralGeometry = new THREE.SphereGeometry(1, 32, 32);
    const centralMaterial = new THREE.MeshPhongMaterial({ 
        color: isDark ? 0x3b82f6 : 0x2563eb,
        shininess: 100,
        transparent: true,
        opacity: 0.9
    });
    const centralNode = new THREE.Mesh(centralGeometry, centralMaterial);
    scene.add(centralNode);
    
    // Create orbiting nodes
    const nodeCount = 8;
    const nodes = [];
    
    for (let i = 0; i < nodeCount; i++) {
        const nodeGeometry = new THREE.SphereGeometry(0.4, 24, 24);
        const nodeMaterial = new THREE.MeshPhongMaterial({ 
            color: isDark ? 
                (i % 3 === 0 ? 0x22d3ee : (i % 3 === 1 ? 0x3b82f6 : 0x8b5cf6)) :
                (i % 3 === 0 ? 0x06b6d4 : (i % 3 === 1 ? 0x3b82f6 : 0x8b5cf6)),
            shininess: 100,
            transparent: true,
            opacity: 0.8
        });
        const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
        
        // Position nodes in a sphere around the center
        const angle = (i / nodeCount) * Math.PI * 2;
        const radius = 5;
        const heightVariation = 3;
        
        node.position.x = Math.cos(angle) * radius;
        node.position.y = Math.sin(angle * 2) * heightVariation;
        node.position.z = Math.sin(angle) * radius;
        
        node.userData = {
            angle: angle,
            radius: radius,
            heightVariation: heightVariation,
            speed: 0.5 + Math.random() * 0.5
        };
        
        nodes.push(node);
        scene.add(node);
        
        // Create connections between nodes
        if (i > 0) {
            const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                nodes[i-1].position,
                node.position
            ]);
            const lineMaterial = new THREE.LineBasicMaterial({ 
                color: isDark ? 0x3b82f6 : 0x2563eb,
                transparent: true,
                opacity: 0.3
            });
            const line = new THREE.Line(lineGeometry, lineMaterial);
            scene.add(line);
        }
        
        // Connect to central node
        const centralLineGeometry = new THREE.BufferGeometry().setFromPoints([
            centralNode.position,
            node.position
        ]);
        const centralLineMaterial = new THREE.LineBasicMaterial({ 
            color: isDark ? 0x22d3ee : 0x06b6d4,
            transparent: true,
            opacity: 0.2
        });
        const centralLine = new THREE.Line(centralLineGeometry, centralLineMaterial);
        scene.add(centralLine);
    }
    
    // Store nodes for animation
    scene.userData = scene.userData || {};
    scene.userData.nodes = nodes;
    scene.userData.centralNode = centralNode;
}

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.offsetWidth / container.offsetHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.offsetWidth, container.offsetHeight);
}

function animate() {
    requestAnimationFrame(animate);
    
    // Rotate the entire scene slowly
    if (scene) {
        scene.rotation.y += 0.001;
        scene.rotation.x += 0.0005;
        
        // Animate nodes
        if (scene.userData && scene.userData.nodes) {
            scene.userData.nodes.forEach((node, i) => {
                const data = node.userData;
                data.angle += 0.005 * data.speed;
                
                node.position.x = Math.cos(data.angle) * data.radius;
                node.position.y = Math.sin(data.angle * 2) * data.heightVariation;
                node.position.z = Math.sin(data.angle) * data.radius;
                
                // Pulsing effect
                const scale = 1 + 0.1 * Math.sin(Date.now() * 0.001 + i);
                node.scale.set(scale, scale, scale);
            });
        }
        
        // Render scene
        renderer.render(scene, camera);
    }
}

// Data Visualization
function initDataVisualization() {
    const container = document.getElementById('viz-container');
    if (!container) return;
    
    const isDark = document.body.classList.contains('dark-theme');
    
    // Create a simple bar chart with D3-like visualization using Three.js
    const vizScene = new THREE.Scene();
    const vizCamera = new THREE.PerspectiveCamera(50, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    const vizRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    vizRenderer.setSize(container.offsetWidth, container.offsetHeight);
    vizRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(vizRenderer.domElement);
    
    // Create bars for visualization
    const barData = [
        { label: 'Week 1', value: 30, color: isDark ? 0x3b82f6 : 0x2563eb },
        { label: 'Week 2', value: 50, color: isDark ? 0x3b82f6 : 0x2563eb },
        { label: 'Week 3', value: 70, color: isDark ? 0x22d3ee : 0x06b6d4 },
        { label: 'Week 4', value: 85, color: isDark ? 0x8b5cf6 : 0x8b5cf6 },
        { label: 'Week 5', value: 95, color: isDark ? 0x10b981 : 0x10b981 }
    ];
    
    const bars = [];
    const barWidth = 0.8;
    const barSpacing = 1.2;
    
    barData.forEach((data, i) => {
        const barHeight = data.value / 20;
        const barGeometry = new THREE.BoxGeometry(barWidth, barHeight, barWidth);
        const barMaterial = new THREE.MeshPhongMaterial({ 
            color: data.color,
            shininess: 100,
            transparent: true,
            opacity: 0.9
        });
        const bar = new THREE.Mesh(barGeometry, barMaterial);
        
        bar.position.x = (i - barData.length / 2) * barSpacing;
        bar.position.y = barHeight / 2;
        
        bar.userData = {
            targetHeight: barHeight,
            currentHeight: 0
        };
        
        bars.push(bar);
        vizScene.add(bar);
        
        // Add bar label
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 128;
        context.fillStyle = isDark ? '#f8fafc' : '#1e293b';
        context.font = 'bold 24px Inter, sans-serif';
        context.textAlign = 'center';
        context.fillText(data.label, 128, 40);
        context.font = '20px Inter, sans-serif';
        context.fillText(`${data.value}%`, 128, 80);
        
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.position.set(bar.position.x, -1.5, 0);
        sprite.scale.set(2, 1, 1);
        vizScene.add(sprite);
    });
    
    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    vizScene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7);
    vizScene.add(directionalLight);
    
    // Position camera
    vizCamera.position.z = 10;
    vizCamera.position.y = 3;
    
    // Add grid
    const gridHelper = new THREE.GridHelper(10, 10, 0x000000, 0x000000);
    gridHelper.material.opacity = 0.1;
    gridHelper.material.transparent = true;
    vizScene.add(gridHelper);
    
    // Animation
    let animationProgress = 0;
    let isAnimating = false;
    
    function animateViz() {
        requestAnimationFrame(animateViz);
        
        // Rotate scene slowly
        vizScene.rotation.y += 0.001;
        
        // Animate bars growing
        if (isAnimating && animationProgress < 1) {
            animationProgress += 0.02;
            bars.forEach((bar, i) => {
                const progress = Math.min(1, animationProgress * 1.5 - i * 0.1);
                const targetHeight = bar.userData.targetHeight;
                const currentHeight = targetHeight * progress;
                
                bar.scale.y = progress;
                bar.position.y = currentHeight / 2;
            });
        }
        
        vizRenderer.render(vizScene, vizCamera);
    }
    
    // Start animation when section is in view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                isAnimating = true;
            }
        });
    }, { threshold: 0.3 });
    
    observer.observe(container);
    
    animateViz();
    
    // Handle resize
    window.addEventListener('resize', () => {
        vizCamera.aspect = container.offsetWidth / container.offsetHeight;
        vizCamera.updateProjectionMatrix();
        vizRenderer.setSize(container.offsetWidth, container.offsetHeight);
    });
}

// Chat Functionality
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const planContainer = document.getElementById('plan-container');
const planDetails = document.getElementById('plan-details');
const timeline = document.getElementById('timeline');

// Conversation flow
const conversationSteps = [
    { question: "What's your name and which grade level are you in?", key: "name_grade" },
    { question: "Which subjects are you struggling with the most? (e.g., Mathematics, Physics, Chemistry, Biology)", key: "subjects" },
    { question: "What are your most urgent deadlines? Please include dates if possible.", key: "deadlines" },
    { question: "On average, how many hours per day can you dedicate to focused study?", key: "studyHours" },
    { question: "On a scale of 1-10, how would you rate your current stress level regarding academics?", key: "stressLevel" },
    { question: "How do you prefer to learn? (Visual, Auditory, Reading/Writing, Kinesthetic, or Mixed)", key: "learningStyle" }
];

let currentStep = 0;
let userData = {};

function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
    messageDiv.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function processUserInput() {
    const input = userInput.value.trim();
    if (!input) return;
    
    // Add user message
    addMessage(input, true);
    
    // Store user response
    const currentKey = conversationSteps[currentStep].key;
    userData[currentKey] = input;
    
    // Clear input
    userInput.value = '';
    
    // Move to next step or generate plan
    currentStep++;
    if (currentStep < conversationSteps.length) {
        setTimeout(() => {
            addMessage(conversationSteps[currentStep].question);
        }, 500);
    } else {
        setTimeout(() => {
            addMessage("Perfect! I have all the information I need. Generating your personalized academic recovery plan now...");
            setTimeout(generatePlan, 1500);
        }, 500);
    }
}

function generatePlan() {
    // Show plan container with animation
    planContainer.style.display = 'block';
    setTimeout(() => {
        planContainer.style.opacity = '1';
        planContainer.style.transform = 'translateY(0)';
    }, 10);
    
    // Scroll to plan
    planContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Generate plan details based on user data
    const subjects = userData.subjects ? userData.subjects.split(',').map(s => s.trim()) : ['Mathematics', 'Science'];
    const studyHours = parseInt(userData.studyHours) || 3;
    const stressLevel = parseInt(userData.stressLevel) || 5;
    const learningStyle = userData.learningStyle || 'Mixed';
    
    // Calculate study allocation
    let studyAllocation = {};
    subjects.forEach((subject, index) => {
        // Allocate more time to first subject (assumed to be most challenging)
        const percentage = index === 0 ? 40 : 60 / (subjects.length - 1);
        studyAllocation[subject] = Math.round((studyHours * percentage / 100) * 10) / 10;
    });
    
    // Generate study schedule based on learning style
    let studyTechnique = "Pomodoro Technique (25 min study, 5 min break)";
    let resources = "Textbooks, Online practice problems, Video tutorials";
    
    if (learningStyle.toLowerCase().includes('visual')) {
        studyTechnique = "Diagrams, Mind maps, Video explanations";
        resources = "Khan Academy videos, Infographics, Whiteboard tutorials";
    } else if (learningStyle.toLowerCase().includes('auditory')) {
        studyTechnique = "Recorded lectures, Discussion groups, Reading aloud";
        resources = "Podcasts, Audiobooks, Study groups";
    } else if (learningStyle.toLowerCase().includes('kinesthetic')) {
        studyTechnique = "Hands-on practice, Lab work, Physical models";
        resources = "Practice kits, Interactive simulations, Real-world applications";
    }
    
    // Generate plan details HTML
    planDetails.innerHTML = `
        <div class="plan-card">
            <h4><i class="fas fa-user-graduate"></i> Student Profile</h4>
            <p><strong>Name/Grade:</strong> ${userData.name_grade || 'Not specified'}</p>
            <p><strong>Learning Style:</strong> ${learningStyle}</p>
            <p><strong>Stress Level:</strong> ${stressLevel}/10</p>
            <p><strong>Study Availability:</strong> ${studyHours} hours/day</p>
        </div>
        <div class="plan-card">
            <h4><i class="fas fa-bullseye"></i> Focus Areas</h4>
            <ul style="list-style: none; padding-left: 0;">
                ${subjects.map(subject => `<li style="margin-bottom: 8px; padding-left: 20px; position: relative;">
                    <i class="fas fa-book" style="position: absolute; left: 0; color: var(--primary);"></i>
                    ${subject}: ${studyAllocation[subject]} hours/day
                </li>`).join('')}
            </ul>
        </div>
        <div class="plan-card">
            <h4><i class="fas fa-lightbulb"></i> Recommended Techniques</h4>
            <p><strong>Primary Method:</strong> ${studyTechnique}</p>
            <p><strong>Resources:</strong> ${resources}</p>
            <p><strong>Breaks:</strong> Every ${stressLevel >= 7 ? '45' : '60'} minutes for ${stressLevel >= 7 ? '15' : '10'}-minute breaks</p>
        </div>
    `;
    
    // Generate timeline
    timeline.innerHTML = `
        <h3 style="margin-bottom: 2rem; color: var(--secondary); font-weight: 600;">Your 4-Week Recovery Roadmap</h3>
        <div class="timeline-item">
            <h4>Week 1-2: Foundation Reinforcement</h4>
            <p>Focus on core concepts in ${subjects[0] || 'priority subjects'}. Complete diagnostic tests to identify specific gaps. Allocate 60% of study time to foundational review.</p>
            <p><strong>Key Activities:</strong> Concept mapping, foundational exercises, weekly progress assessment</p>
        </div>
        <div class="timeline-item">
            <h4>Week 3: Application & Practice</h4>
            <p>Apply learned concepts to practice problems and past papers. Begin integrating ${subjects.length > 1 ? subjects[1] : 'secondary subjects'} into study schedule.</p>
            <p><strong>Key Activities:</strong> Practice tests, timed exercises, concept application projects</p>
        </div>
        <div class="timeline-item">
            <h4>Week 4: Integration & Mastery</h4>
            <p>Synthesize knowledge across subjects. Focus on exam techniques and time management. Conduct full-length mock exams under timed conditions.</p>
            <p><strong>Key Activities:</strong> Mock exams, review sessions, stress management techniques</p>
        </div>
    `;
    
    // Add a final message to chat
    setTimeout(() => {
        addMessage("Your personalized academic recovery plan is ready! I've created a detailed roadmap with specific weekly goals, study techniques matched to your learning style, and stress management strategies. The plan adapts based on your progress - check back weekly for adjustments.");
    }, 1000);
}

// Event Listeners
sendBtn.addEventListener('click', processUserInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') processUserInput();
});

document.getElementById('start-btn').addEventListener('click', () => {
    document.getElementById('chat').scrollIntoView({ behavior: 'smooth' });
});

document.getElementById('hero-start-btn').addEventListener('click', () => {
    document.getElementById('chat').scrollIntoView({ behavior: 'smooth' });
});

document.getElementById('download-plan').addEventListener('click', () => {
    alert("Plan downloaded! Check your downloads folder for 'My-StudySync-Plan.pdf'");
});

document.getElementById('schedule-plan').addEventListener('click', () => {
    alert("Study sessions have been added to your calendar. You'll receive reminders before each session.");
});

// Mobile menu toggle
document.querySelector('.mobile-menu').addEventListener('click', () => {
    const nav = document.querySelector('nav ul');
    nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
});

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    createBackgroundAnimation();
    init3DAnimation();
    initDataVisualization();
    
    // Start conversation
    setTimeout(() => {
        addMessage(conversationSteps[currentStep].question);
    }, 1000);
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('nav a, .footer-links a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId.startsWith('#')) {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    // Close mobile menu if open
                    if (window.innerWidth <= 992) {
                        document.querySelector('nav ul').style.display = 'none';
                    }
                    
                    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
    
    // Header scroll effect
    window.addEventListener('scroll', () => {
        const header = document.querySelector('header');
        if (window.scrollY > 50) {
            header.style.padding = '0.8rem 5%';
            header.style.boxShadow = '0 5px 20px var(--shadow-color)';
        } else {
            header.style.padding = '1.2rem 5%';
            header.style.boxShadow = '0 1px 3px var(--shadow-color)';
        }
    });
    
    // Theme change observer
    const themeObserver = new MutationObserver(() => {
        createBackgroundAnimation();
    });
    
    themeObserver.observe(document.body, {
        attributes: true,
        attributeFilter: ['class']
    });
});

// ========== 🍅 POMODORO TIMER (CUSTOM SOUND SUPPORT) ==========
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const pomodoroToggle = document.getElementById('pomodoro-toggle');
    const pomodoroCard = document.getElementById('pomodoro-card');
    const pomodoroClose = document.getElementById('pomodoro-close');
    const minutesEl = document.getElementById('pomodoro-minutes');
    const secondsEl = document.getElementById('pomodoro-seconds');
    const modeEl = document.getElementById('pomodoro-mode');
    const startBtn = document.getElementById('pomodoro-start');
    const pauseBtn = document.getElementById('pomodoro-pause');
    const resetBtn = document.getElementById('pomodoro-reset');
    const workInput = document.getElementById('pomodoro-work');
    const breakInput = document.getElementById('pomodoro-break');
    const applyBtn = document.getElementById('pomodoro-apply');
    
    // Custom Sound Elements
    const soundInput = document.getElementById('pomodoro-sound');
    const soundFilename = document.getElementById('sound-filename');
    let customAudioUrl = null;

    if (!pomodoroToggle || !pomodoroCard) return;

    // Sound notification function
    function playCompletionSound() {
        if (customAudioUrl) {
            try {
                const audio = new Audio(customAudioUrl);
                audio.play().catch(e => console.log('Audio play failed:', e));
            } catch (e) {
                console.log('Error playing custom sound:', e);
            }
        }
        // No fallback sound (optional – you can enable the beep if you want)
    }

    // Handle Custom Sound Upload
    if (soundInput && soundFilename) {
        soundInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (customAudioUrl) URL.revokeObjectURL(customAudioUrl);
                customAudioUrl = URL.createObjectURL(file);
                soundFilename.textContent = file.name.length > 20 ? file.name.substring(0, 17) + '...' : file.name;
            } else {
                if (customAudioUrl) URL.revokeObjectURL(customAudioUrl);
                customAudioUrl = null;
                soundFilename.textContent = 'No file selected';
            }
        });
    }

    // Toggle Pomodoro card
    pomodoroToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        pomodoroCard.style.display = pomodoroCard.style.display === 'block' ? 'none' : 'block';
    });

    // Close card
    if (pomodoroClose) {
        pomodoroClose.addEventListener('click', function() {
            pomodoroCard.style.display = 'none';
        });
    }

    // Close card when clicking outside
    window.addEventListener('click', function(e) {
        if (!pomodoroCard.contains(e.target) && e.target !== pomodoroToggle && !pomodoroToggle.contains(e.target)) {
            pomodoroCard.style.display = 'none';
        }
    });

    pomodoroCard.addEventListener('click', function(e) { e.stopPropagation(); });

    // Timer logic
    if (minutesEl && secondsEl && modeEl && startBtn && pauseBtn && resetBtn && workInput && breakInput && applyBtn) {
        let workTime = parseInt(workInput.value) || 25;
        let breakTime = parseInt(breakInput.value) || 5;
        let minutes = workTime;
        let seconds = 0;
        let timer = null;
        let mode = 'work';

        function updateDisplay() {
            minutesEl.textContent = minutes.toString().padStart(2, '0');
            secondsEl.textContent = seconds.toString().padStart(2, '0');
        }

        function switchMode() {
            if (mode === 'work') {
                mode = 'break';
                minutes = breakTime;
                seconds = 0;
                modeEl.textContent = 'Break';
            } else {
                mode = 'work';
                minutes = workTime;
                seconds = 0;
                modeEl.textContent = 'Work';
            }
            updateDisplay();
        }

        function startTimer() {
            if (timer) return;
            timer = setInterval(() => {
                if (seconds === 0) {
                    if (minutes === 0) {
                        playCompletionSound(); // 🔔 SOUND HERE
                        clearInterval(timer);
                        timer = null;
                        switchMode();
                        startTimer();
                        return;
                    } else {
                        minutes--;
                        seconds = 59;
                    }
                } else {
                    seconds--;
                }
                updateDisplay();
            }, 1000);
        }

        function pauseTimer() {
            clearInterval(timer);
            timer = null;
        }

        function resetTimer() {
            pauseTimer();
            mode = 'work';
            modeEl.textContent = 'Work';
            minutes = workTime;
            seconds = 0;
            updateDisplay();
        }

        function applySettings() {
            let newWork = parseInt(workInput.value);
            let newBreak = parseInt(breakInput.value);
            if (isNaN(newWork) || newWork < 1) workInput.value = 1;
            if (isNaN(newBreak) || newBreak < 1) breakInput.value = 1;
            workTime = parseInt(workInput.value) || 25;
            breakTime = parseInt(breakInput.value) || 5;
            resetTimer();
        }

        startBtn.addEventListener('click', startTimer);
        pauseBtn.addEventListener('click', pauseTimer);
        resetBtn.addEventListener('click', resetTimer);
        applyBtn.addEventListener('click', applySettings);

        workInput.addEventListener('change', function() {
            let val = parseInt(this.value);
            if (isNaN(val) || val < 1) this.value = 1;
            if (val > 60) this.value = 60;
        });
        breakInput.addEventListener('change', function() {
            let val = parseInt(this.value);
            if (isNaN(val) || val < 1) this.value = 1;
            if (val > 30) this.value = 30;
        });

        updateDisplay();
    }
});

// ========== NEW: CHAT ➕ BUTTON TOGGLE ==========
document.addEventListener('DOMContentLoaded', function() {
    const plusBtn = document.getElementById('chat-plus-btn');
    const popup = document.getElementById('chat-plus-popup');

    if (plusBtn && popup) {
        // Toggle popup on button click
        plusBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            popup.style.display = popup.style.display === 'block' ? 'none' : 'block';
        });

        // Close popup when clicking outside
        window.addEventListener('click', function(e) {
            if (!popup.contains(e.target) && e.target !== plusBtn && !plusBtn.contains(e.target)) {
                popup.style.display = 'none';
            }
        });

        // Prevent popup from closing when clicking inside it
        popup.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});