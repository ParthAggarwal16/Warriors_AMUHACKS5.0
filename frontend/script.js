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
    
    // Check if shapes exist to avoid recreating them (smoother transition)
    if (container.children.length === 0) {
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
    } else {
        // Update colors of existing shapes
        Array.from(container.children).forEach(shape => {
            const color = colors[Math.floor(Math.random() * colors.length)];
            shape.style.background = color;
        });
    }
}

// Professional 3D Animation for Hero Section
let scene, camera, renderer;
let mouseX = 0;
let mouseY = 0;

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
    
    // Track mouse movement for interaction
    document.addEventListener('mousemove', (event) => {
        mouseX = event.clientX - window.innerWidth / 2;
        mouseY = event.clientY - window.innerHeight / 2;
    });
    
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
        
        // Interactive Camera Movement (Parallax Effect)
        // Smoothly move camera based on mouse position
        camera.position.x += (mouseX * 0.005 - camera.position.x) * 0.05;
        camera.position.y += (-(mouseY * 0.005) + 5 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);
        
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
        { label: 'Stress', value: 10, color: isDark ? 0xef4444 : 0xef4444 },
        { label: 'Hours', value: 10, color: isDark ? 0x3b82f6 : 0x2563eb },
        { label: 'Load', value: 10, color: isDark ? 0x10b981 : 0x10b981 }
    ];
    
    const bars = [];
    const sprites = []; // Track sprites to update labels
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
        // Initial empty value
        // context.fillText(`${data.value}%`, 128, 80);
        
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.position.set(bar.position.x, -1.5, 0);
        sprite.scale.set(2, 1, 1);
        sprites.push(sprite);
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

    // Expose update function globally
    window.updateVizData = function(data) {
        const stress = parseInt(data.stressLevel) || 5;
        const hours = parseInt(data.studyHours) || 2;
        const subjects = data.subjects ? data.subjects.split(',').length : 3;
        
        const metrics = [
            { label: 'Stress', value: stress * 10, color: stress > 7 ? 0xef4444 : 0x10b981 }, // Red if high stress
            { label: 'Hours', value: Math.min(hours * 10, 100), color: 0x3b82f6 },
            { label: 'Load', value: Math.min(subjects * 20, 100), color: 0xf59e0b }
        ];
        
        const isDark = document.body.classList.contains('dark-theme');

        metrics.forEach((metric, i) => {
            if (bars[i]) {
                // Update bar height target
                bars[i].userData.targetHeight = Math.max(0.5, metric.value / 20);
                bars[i].material.color.setHex(metric.color);
                
                // Update label
                if (sprites[i]) {
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    canvas.width = 256;
                    canvas.height = 128;
                    context.fillStyle = isDark ? '#f8fafc' : '#1e293b';
                    context.font = 'bold 24px Inter, sans-serif';
                    context.textAlign = 'center';
                    context.fillText(metric.label, 128, 40);
                    context.font = '20px Inter, sans-serif';
                    
                    let valueText = "";
                    if (i === 0) valueText = `${stress}/10`;
                    else if (i === 1) valueText = `${hours}h/day`;
                    else valueText = `${subjects} Subj`;
                    
                    context.fillText(valueText, 128, 80);
                    
                    const texture = new THREE.CanvasTexture(canvas);
                    sprites[i].material.map = texture;
                }
            }
        });
        
        // Restart animation
        animationProgress = 0;
        isAnimating = true;
    };
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
let currentPlanData = null;

function addMessage(message, isUser = false, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
    messageDiv.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'typing-indicator';
    spinner.id = 'loading-spinner';
    spinner.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    chatMessages.appendChild(spinner);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.remove();
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
            
            setTimeout(() => {
                showLoadingSpinner();
                setTimeout(() => {
                    hideLoadingSpinner();
                    
                    // Generate mock plan data locally based on user inputs
                    const subjectsList = userData.subjects ? userData.subjects.split(',').map(s => s.trim()) : ['General Studies'];
                    const studyHours = parseInt(userData.studyHours) || 2;
                    
                    const planData = {
                        profile: {
                            name: userData.name_grade || 'Student',
                            style: userData.learningStyle || 'Mixed',
                            stress: userData.stressLevel || '5',
                            hours: studyHours + ' hours/day'
                        },
                        focus_areas: subjectsList.map(s => ({
                            subject: s,
                            hours: (studyHours / Math.max(1, subjectsList.length)).toFixed(1) + ' hours/day',
                            focus: 'Core concepts and practice problems'
                        })),
                        techniques: {
                            primary: userData.learningStyle && userData.learningStyle.toLowerCase().includes('visual') ? 'Mind Mapping & Diagrams' : 'Pomodoro Technique',
                            resources: 'Textbooks, Online Videos, Practice Papers',
                            break_strategy: parseInt(userData.stressLevel) > 7 ? 'Frequent short breaks (25/5)' : 'Standard breaks (50/10)'
                        },
                        timeline: [
                            { week: 'Week 1', title: 'Foundations', desc: 'Review core concepts in ' + (subjectsList[0] || 'key subjects'), activities: 'Diagnostic tests, summary notes' },
                            { week: 'Week 2', title: 'Deep Dive', desc: 'Focus on difficult topics and weak areas', activities: 'Practice problems, active recall sessions' },
                            { week: 'Week 3', title: 'Application', desc: 'Apply knowledge to past papers and complex problems', activities: 'Timed quizzes, peer review' },
                            { week: 'Week 4', title: 'Mastery', desc: 'Final review and mock exams', activities: 'Full mock exam, error analysis' }
                        ]
                    };
                    
                    renderPlan(planData);
                }, 1500);
            }, 500);
        }, 500);
    }
}

// Function to save plan to backend
async function savePlanToBackend(planData) {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || !user.email) return; // Only save if logged in

    try {
        await fetch('/api/save-plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: user.email,
                plan_data: planData
            })
        });
        console.log('Plan saved to database');
    } catch (error) {
        console.error('Error saving plan:', error);
    }
}

function renderPlan(planData) {
    currentPlanData = planData;
    // Show plan container with animation
    planContainer.style.display = 'block';
    setTimeout(() => {
        planContainer.style.opacity = '1';
        planContainer.style.transform = 'translateY(0)';
    }, 10);
    
    // Scroll to plan
    planContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Generate plan details HTML
    planDetails.innerHTML = `
        <div class="plan-card">
            <h4><i class="fas fa-user-graduate"></i> Student Profile</h4>
            <p><strong>Name/Grade:</strong> ${planData.profile.name}</p>
            <p><strong>Learning Style:</strong> ${planData.profile.style}</p>
            <p><strong>Stress Level:</strong> ${planData.profile.stress}/10</p>
            <p><strong>Study Availability:</strong> ${planData.profile.hours}</p>
        </div>
        <div class="plan-card">
            <h4><i class="fas fa-bullseye"></i> Focus Areas</h4>
            <ul style="list-style: none; padding-left: 0;">
                ${planData.focus_areas.map(area => `<li style="margin-bottom: 8px; padding-left: 20px; position: relative;">
                    <i class="fas fa-book" style="position: absolute; left: 0; color: var(--primary);"></i>
                    ${area.subject}: ${area.hours} - ${area.focus}
                </li>`).join('')}
            </ul>
        </div>
        <div class="plan-card">
            <h4><i class="fas fa-lightbulb"></i> Recommended Techniques</h4>
            <p><strong>Primary Method:</strong> ${planData.techniques.primary}</p>
            <p><strong>Resources:</strong> ${planData.techniques.resources}</p>
            <p><strong>Breaks:</strong> ${planData.techniques.break_strategy}</p>
        </div>
    `;
    
    // Generate timeline
    timeline.innerHTML = `
        <h3 style="margin-bottom: 2rem; color: var(--secondary); font-weight: 600;">Your 4-Week Recovery Roadmap</h3>
        ${planData.timeline.map(item => `
        <div class="timeline-item">
            <h4>${item.week}: ${item.title}</h4>
            <p>${item.desc}</p>
            <p><strong>Key Activities:</strong> ${item.activities}</p>
        </div>
        `).join('')}
    `;
    
    // Add a final message to chat
    setTimeout(() => {
        addMessage("Your personalized academic recovery plan is ready! I've created a detailed roadmap with specific weekly goals, study techniques matched to your learning style, and stress management strategies. The plan adapts based on your progress - check back weekly for adjustments.");
    }, 1000);

    // Save to backend
    savePlanToBackend(planData);

    // Update Analytics Visualization
    if (window.updateVizData) {
        window.updateVizData(userData);
    }
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
    if (currentPlanData) {
        downloadICS(currentPlanData);
        alert("Study schedule exported! Open the downloaded .ics file to add it to your calendar.");
    } else {
        alert("Please generate a plan first.");
    }
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

    // Check auth status on load
    updateAuthUI();
});

// Authentication Modal Functionality
const authModal = document.getElementById('auth-modal');
let navLoginBtn = document.getElementById('nav-login-btn');

const closeModal = document.querySelector('.close-modal');
const tabBtns = document.querySelectorAll('.tab-btn');
const authForms = document.querySelectorAll('.auth-form');

// Update UI based on auth state
function updateAuthUI() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user'));
    const userMenu = document.getElementById('user-menu');
    const userNameDisplay = document.getElementById('user-name-display');
    
    // Cleanup old greeting if it exists
    const oldGreeting = document.getElementById('nav-greeting');
    if (oldGreeting) oldGreeting.remove();

    if (navLoginBtn && userMenu) {
        if (token && user) {
            // Logged In: Hide login button, show user menu
            navLoginBtn.style.display = 'none';
            userMenu.style.display = 'block';
            if (userNameDisplay) {
                userNameDisplay.textContent = user.name.split(' ')[0];
            }
        } else {
            // Logged Out: Show login button, hide user menu
            navLoginBtn.style.display = 'block';
            navLoginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
            userMenu.style.display = 'none';
        }
    }
}

// User Menu Dropdown Toggle
const userMenuBtn = document.getElementById('user-menu-btn');
const userMenu = document.getElementById('user-menu');

if (userMenuBtn) {
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userMenu.classList.toggle('active');
    });
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (userMenu && userMenu.classList.contains('active')) {
        if (!userMenu.contains(e.target)) {
            userMenu.classList.remove('active');
        }
    }
});

// Load plan from backend
async function loadUserPlan() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || !user.email) return;

    try {
        const response = await fetch(`/api/get-plan?email=${encodeURIComponent(user.email)}`);
        if (response.ok) {
            const data = await response.json();
            if (data.plan_data) {
                // Skip chat and show plan immediately
                document.getElementById('chat').scrollIntoView({ behavior: 'smooth' });
                
                // Fill chat with a welcome back message
                chatMessages.innerHTML = '';
                addMessage(`Welcome back, ${user.name}! I've loaded your saved recovery plan.`);
                
                renderPlan(data.plan_data);
            }
        }
    } catch (error) {
        console.error('Error loading plan:', error);
    }
}

// Handle Logout
async function handleLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
    } catch (error) {
        console.error('Logout failed:', error);
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    updateAuthUI();
    alert('Logged out successfully');
    
    // Hide plan on logout
    planContainer.style.display = 'none';
    // Reset chat
    location.reload(); 
}

// Logout Link in Dropdown
const logoutLink = document.getElementById('logout-link');
if (logoutLink) {
    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        handleLogout();
        if (userMenu) userMenu.classList.remove('active');
    });
}

// Open Modal or Logout
if (navLoginBtn) {
    navLoginBtn.addEventListener('click', () => {
        const token = localStorage.getItem('token');
        if (token) {
            handleLogout();
        } else {
            authModal.style.display = 'flex';
            // Small delay for animation
            setTimeout(() => {
                authModal.classList.add('show');
            }, 10);
        }
    });
}

// Close Modal
if (closeModal) {
    closeModal.addEventListener('click', () => {
        authModal.classList.remove('show');
        setTimeout(() => {
            authModal.style.display = 'none';
        }, 300);
    });
}

// Switch Tabs (Login/Signup)
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all buttons and forms
        tabBtns.forEach(b => b.classList.remove('active'));
        authForms.forEach(f => f.classList.remove('active'));
        
        // Add active class to clicked button
        btn.classList.add('active');
        
        // Show corresponding form
        const tabId = btn.getAttribute('data-tab');
        document.getElementById(`${tabId}-form`).classList.add('active');
    });
});

// Forgot Password / Back to Login Navigation
const forgotPasswordLink = document.getElementById('forgot-password-link');
const backToLoginLink = document.getElementById('back-to-login');
const forgotPasswordForm = document.getElementById('forgot-password-form');
const authTabs = document.querySelector('.auth-tabs');

if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener('click', (e) => {
        e.preventDefault();
        authForms.forEach(f => f.classList.remove('active'));
        forgotPasswordForm.classList.add('active');
        if (authTabs) authTabs.style.display = 'none';
    });
}

if (backToLoginLink) {
    backToLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        authForms.forEach(f => f.classList.remove('active'));
        document.getElementById('login-form').classList.add('active');
        if (authTabs) authTabs.style.display = 'flex';
    });
}

// Validation Helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

function showError(input, message) {
    const formGroup = input.parentElement;
    const error = document.createElement('div');
    error.className = 'error-message';
    error.innerText = message;
    formGroup.appendChild(error);
    input.classList.add('input-error');
}

function clearErrors(form) {
    const errors = form.querySelectorAll('.error-message');
    errors.forEach(e => e.remove());
    const inputs = form.querySelectorAll('.input-error');
    inputs.forEach(i => i.classList.remove('input-error'));
}

// Handle Form Submission (Demo)
authForms.forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous errors
        clearErrors(form);
        
        let isValid = true;
        const formId = form.id;
        
        // Validate based on form type
        if (formId === 'login-form') {
            const email = form.querySelector('#login-email');
            const password = form.querySelector('#login-password');
            
            if (!validateEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            }
            
            if (password.value.length < 6) {
                showError(password, 'Password must be at least 6 characters');
                isValid = false;
            }
        } else if (formId === 'forgot-password-form') {
            const email = form.querySelector('#forgot-email');
            
            if (!validateEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            }
        } else if (formId === 'signup-form') {
            const name = form.querySelector('#signup-name');
            const email = form.querySelector('#signup-email');
            const password = form.querySelector('#signup-password');
            
            if (name.value.trim().length < 2) {
                showError(name, 'Name must be at least 2 characters');
                isValid = false;
            }
            
            if (!validateEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            }
            
            if (password.value.length < 6) {
                showError(password, 'Password must be at least 6 characters');
                isValid = false;
            }
        }
        
        if (!isValid) return;

        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        
        btn.innerText = 'Processing...';
        btn.style.opacity = '0.7';
        btn.disabled = true;
        
        // Prepare data for backend
        const payload = {};
        if (formId === 'login-form') {
            payload.email = form.querySelector('#login-email').value;
            payload.password = form.querySelector('#login-password').value;
        } else if (formId === 'signup-form') {
            payload.name = form.querySelector('#signup-name').value;
            payload.email = form.querySelector('#signup-email').value;
            payload.password = form.querySelector('#signup-password').value;
        } else if (formId === 'forgot-password-form') {
            payload.email = form.querySelector('#forgot-email').value;
        }

        // API Endpoint (Assumes backend is running on localhost:3000)
        let endpoint = '/api/signup';
        if (formId === 'login-form') endpoint = '/api/login';
        else if (formId === 'forgot-password-form') endpoint = '/api/forgot-password';

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Authentication failed');
            }

            btn.innerText = 'Success!';
            btn.style.background = 'var(--success)';
            
            // Store auth token if returned
            if (data.token) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                updateAuthUI();
                loadUserPlan(); // Load their plan immediately after login
            } else if (formId === 'forgot-password-form') {
                alert(data.message);
                // Optional: switch back to login automatically
            }
            
            setTimeout(() => {
                authModal.classList.remove('show');
                setTimeout(() => {
                    authModal.style.display = 'none';
                    btn.innerText = originalText;
                    btn.style.background = '';
                    btn.style.opacity = '1';
                    btn.disabled = false;
                }, 300);
            }, 1000);

        } catch (error) {
            btn.innerText = originalText;
            btn.style.opacity = '1';
            btn.style.background = '';
            btn.disabled = false;
            
            // Show error message
            const errorInput = formId === 'login-form' 
                ? form.querySelector('#login-email') 
                : (formId === 'signup-form' 
                    ? form.querySelector('#signup-email') 
                    : form.querySelector('#forgot-email'));
            showError(errorInput, error.message);
        }
    });
});

// Generate and download ICS file
function downloadICS(planData) {
    if (!planData || !planData.timeline) return;

    let icsContent = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//StudySync Pro//NONSGML v1.0//EN\nCALSCALE:GREGORIAN\nMETHOD:PUBLISH\n";
    
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1); // Start tomorrow

    planData.timeline.forEach((item, index) => {
        const eventDate = new Date(startDate);
        eventDate.setDate(startDate.getDate() + (index * 7));
        
        const dateString = eventDate.toISOString().split('T')[0].replace(/-/g, '');
        const uid = `studysync-${Date.now()}-${index}`;
        const dtstamp = new Date().toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
        
        icsContent += "BEGIN:VEVENT\n";
        icsContent += `UID:${uid}\n`;
        icsContent += `DTSTAMP:${dtstamp}\n`;
        icsContent += `DTSTART;VALUE=DATE:${dateString}\n`;
        icsContent += `SUMMARY:StudySync: ${item.title}\n`;
        icsContent += `DESCRIPTION:${item.desc}\\n\\nActivities: ${item.activities}\n`;
        icsContent += "END:VEVENT\n";
    });

    icsContent += "END:VCALENDAR";

    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.setAttribute('download', 'StudySync_Plan.ics');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}