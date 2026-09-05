// MediKiosk Interactive Flow Controller & Voice Integration
let currentStageIndex = 0;
let currentScreenIndex = 0;
let flatScreensList = [];

// Initialize flat list of screens for sequential linear navigation
FLOW_STAGES.forEach((stage, sIdx) => {
    stage.screens.forEach((scr, scrIdx) => {
        flatScreensList.push({
            ...scr,
            stageKey: stage.key,
            stageName: stage.name,
            stageIndex: sIdx,
            screenIndexInStage: scrIdx
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    buildSidebarNavigator();
    loadScreen(0);
});

function buildSidebarNavigator() {
    const container = document.getElementById('screenListContainer');
    if (!container) return;
    container.innerHTML = '';

    FLOW_STAGES.forEach((stage, sIdx) => {
        // Stage Header
        const stageHeader = document.createElement('div');
        stageHeader.className = 'px-4 py-2 bg-surface-container/60 text-[11px] font-bold text-primary flex items-center justify-between tracking-wide uppercase';
        stageHeader.innerHTML = `<span>${stage.name.split(':')[0]}</span><span class="text-on-surface-variant/60 font-normal">${stage.screens.length}</span>`;
        container.appendChild(stageHeader);

        // Screens under this stage
        stage.screens.forEach(screen => {
            const globalIndex = flatScreensList.findIndex(s => s.id === screen.id);
            const item = document.createElement('button');
            item.id = `nav-item-${globalIndex}`;
            item.className = `w-full text-left px-4 py-2.5 flex items-start gap-2.5 transition-colors hover:bg-surface-container/80 text-on-surface border-l-4 border-transparent`;
            item.onclick = () => loadScreen(globalIndex);

            item.innerHTML = `
                <span class="w-5 h-5 rounded-full bg-surface-container-high flex items-center justify-center text-[10px] font-bold text-on-surface-variant shrink-0 mt-0.5">
                    ${globalIndex + 1}
                </span>
                <div class="flex-1 min-w-0">
                    <p class="font-headline font-semibold text-xs truncate leading-snug">${screen.title.split('—')[0].trim()}</p>
                    <p class="text-[11px] text-on-surface-variant truncate">${screen.title.split('—')[1] ? screen.title.split('—')[1].trim() : screen.description}</p>
                </div>
            `;
            container.appendChild(item);
        });
    });
}

function loadScreen(index) {
    if (index < 0 || index >= flatScreensList.length) return;
    currentScreenIndex = index;
    const target = flatScreensList[index];

    // Update screen frame
    const iframe = document.getElementById('screenFrame');
    iframe.style.opacity = '0';
    setTimeout(() => {
        iframe.src = `screens/${target.file}`;
        iframe.onload = () => {
            iframe.style.opacity = '1';
            injectEnglishLocalization(iframe);
            bindFrameInteractions(iframe, target);
        };
    }, 150);

    // Update Top App Bar & Status
    document.getElementById('activeScreenBadge').textContent = target.stageKey;
    document.getElementById('activeScreenTitle').textContent = `${index + 1}. ${target.title}`;
    document.getElementById('screenCounter').textContent = `Screen ${index + 1} of ${flatScreensList.length}`;

    // Update Stepper buttons
    document.querySelectorAll('.stage-pill').forEach(pill => {
        if (pill.getAttribute('data-stage') === target.stageKey) {
            pill.className = 'stage-pill px-3 py-1 rounded-full font-medium transition-all bg-on-primary text-primary';
        } else {
            pill.className = 'stage-pill px-3 py-1 rounded-full font-medium transition-all text-on-primary hover:bg-on-primary/10';
        }
    });

    // Update Active Navigation item in sidebar
    flatScreensList.forEach((_, idx) => {
        const el = document.getElementById(`nav-item-${idx}`);
        if (el) {
            if (idx === index) {
                el.className = 'w-full text-left px-4 py-2.5 flex items-start gap-2.5 bg-primary/10 text-primary font-bold border-l-4 border-primary';
                el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                el.className = 'w-full text-left px-4 py-2.5 flex items-start gap-2.5 transition-colors hover:bg-surface-container/80 text-on-surface border-l-4 border-transparent';
            }
        }
    });

    // Update Voice Assistant Context Caption
    updateVoiceContext(target);
}

function nextScreen() {
    if (currentScreenIndex < flatScreensList.length - 1) {
        loadScreen(currentScreenIndex + 1);
    }
}

function prevScreen() {
    if (currentScreenIndex > 0) {
        loadScreen(currentScreenIndex - 1);
    }
}

function goToStage(stageKey) {
    const targetIdx = flatScreensList.findIndex(s => s.stageKey === stageKey);
    if (targetIdx !== -1) {
        loadScreen(targetIdx);
    }
}

function openScreenByKey(screenId) {
    const idx = flatScreensList.findIndex(s => s.id === screenId);
    if (idx !== -1) {
        loadScreen(idx);
        closeEmergencyOverlay();
    }
}

// Clean English localization & wire up next buttons inside screen templates
function injectEnglishLocalization(iframe) {
    try {
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        if (!doc) return;

        // Clean any bilingual remnants
        doc.querySelectorAll('*').forEach(el => {
            if (el.children.length === 0 && el.textContent) {
                if (el.textContent.includes('अपनी भाषा चुनें')) {
                    el.textContent = 'Choose your language';
                }
                if (el.textContent.includes('यहाँ शुरू करें')) {
                    el.textContent = '';
                }
                if (el.textContent.includes('आगे बढ़ें / Next') || el.textContent.includes('आगे बढ़ें')) {
                    el.textContent = 'Next / Continue';
                }
            }
        });

        // Interactive Button Wiring to advance to next screen seamlessly
        const actionButtons = doc.querySelectorAll('button, [role="button"]');
        actionButtons.forEach(btn => {
            const txt = (btn.textContent || '').trim().toLowerCase();
            
            // Language screen: clicking English card or Next button
            if (txt.includes('english')) {
                btn.addEventListener('click', () => {
                    setTimeout(() => { nextScreen(); }, 500);
                });
            }
            
            // Start / Continue / Next buttons
            if (txt.includes('tap to start') || txt.includes('start') || txt.includes('continue') || txt.includes('next') || txt.includes('proceed')) {
                btn.addEventListener('click', (e) => {
                    // Check if it's an emergency button
                    if (txt.includes('emergency') || txt.includes('sos')) {
                        triggerEmergencyOverlay();
                        return;
                    }
                    setTimeout(() => { nextScreen(); }, 600);
                });
            }

            // Back buttons
            if (txt.includes('back')) {
                btn.addEventListener('click', () => {
                    setTimeout(() => { prevScreen(); }, 300);
                });
            }

            // Emergency / SOS buttons inside iframes
            if (txt.includes('emergency') || txt.includes('sos')) {
                btn.addEventListener('click', () => {
                    triggerEmergencyOverlay();
                });
            }
        });

    } catch (e) {
        console.warn('Iframe inspection note:', e);
    }
}

function bindFrameInteractions(iframe, currentScreen) {
    try {
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        if (!doc) return;

        // PainMapper: Interactive body pain dots and slider feedback
        if (currentScreen.id === 'pain_mapper') {
            const slider = doc.querySelector('input[type=range]');
            if (slider) {
                slider.addEventListener('input', (e) => {
                    const caption = document.getElementById('voiceLiveCaption');
                    if (caption) {
                        caption.innerHTML = `<span class="text-primary font-bold">🎙 Pain Slider:</span> "Intensity set to ${e.target.value}/10"`;
                    }
                });
            }

            // Make body image interactive: clicking on it adds a pulsing red pain dot
            const bodyContainer = doc.querySelector('.relative.w-full.max-w-sm');
            if (bodyContainer) {
                bodyContainer.style.cursor = 'crosshair';
                bodyContainer.addEventListener('click', (e) => {
                    const rect = bodyContainer.getBoundingClientRect();
                    const xPercent = ((e.clientX - rect.left) / rect.width) * 100;
                    const yPercent = ((e.clientY - rect.top) / rect.height) * 100;

                    const dot = doc.createElement('div');
                    dot.className = 'absolute w-8 h-8 bg-error rounded-full pulse-dot z-20 cursor-pointer border-4 border-on-error shadow-lg';
                    dot.style.top = `${yPercent}%`;
                    dot.style.left = `${xPercent}%`;
                    dot.style.transform = 'translate(-50%, -50%)';
                    dot.title = 'Selected Pain Site';
                    dot.onclick = (event) => {
                        event.stopPropagation();
                        dot.remove();
                    };
                    bodyContainer.appendChild(dot);

                    const caption = document.getElementById('voiceLiveCaption');
                    if (caption) {
                        caption.innerHTML = `<span class="text-primary font-bold">🎙 Pain Area Added:</span> "Marked pain point on body diagram"`;
                    }
                });
            }
        }

        // VoiceOrb: Clicking Stop button advances to PainMapper
        if (currentScreen.id === 'voice_orb') {
            const stopBtn = doc.querySelector('footer button.bg-error');
            if (stopBtn) {
                stopBtn.addEventListener('click', () => {
                    setTimeout(() => { openScreenByKey('pain_mapper'); }, 400);
                });
            }
        }

    } catch (e) {}
}

function updateVoiceContext(screen) {
    const caption = document.getElementById('voiceLiveCaption');
    if (!caption) return;

    if (screen.id === 'voice_orb') {
        caption.innerHTML = '<span class="text-primary font-bold">🎙 Listening:</span> "I have had severe chest discomfort for two hours..."';
    } else if (screen.id === 'pain_mapper') {
        caption.innerHTML = '<span class="text-primary font-bold">🎙 Voice/Touch:</span> "Tap body diagram to mark pain spot or say: It hurts in my chest"';
    } else if (screen.id === 'chief_complaint') {
        caption.innerHTML = '<span class="text-primary font-bold">🎙 Assistant:</span> "Please state your primary health concern today"';
    } else if (screen.id === 'socrates_engine') {
        caption.innerHTML = '<span class="text-primary font-bold">🎙 Assistant:</span> "Does the pain radiate to your left arm, neck, or back?"';
    } else {
        caption.innerHTML = `<span>Voice Engine Active on <strong>${screen.title.split('—')[0]}</strong></span>`;
    }
}

function simulateVoiceInput(transcribedText) {
    const caption = document.getElementById('voiceLiveCaption');
    if (caption) {
        caption.innerHTML = `<span class="text-primary font-bold">🎙 Speech Captured:</span> "${transcribedText}"`;
    }

    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance("Captured voice intake: " + transcribedText);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }

    // Contextual voice routing: if on VoiceOrb or Welcome screen, advance to PainMapper
    if (flatScreensList[currentScreenIndex].id === 'voice_orb' || flatScreensList[currentScreenIndex].id === 'chief_complaint' || flatScreensList[currentScreenIndex].id === 'welcome_gate') {
        setTimeout(() => {
            openScreenByKey('pain_mapper');
        }, 1500);
    }
}

function speakCurrentScreenPrompt() {
    const target = flatScreensList[currentScreenIndex];
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(target.title.split('—')[0] + ". " + target.description);
        window.speechSynthesis.speak(utterance);
    }
}

function triggerEmergencyOverlay() {
    const modal = document.getElementById('emergencyModal');
    if (modal) modal.classList.remove('hidden');
}

function closeEmergencyOverlay() {
    const modal = document.getElementById('emergencyModal');
    if (modal) modal.classList.add('hidden');
}

function toggleSidebarCompact() {
    const sidebar = document.querySelector('aside');
    if (sidebar) {
        sidebar.classList.toggle('hidden');
    }
}
