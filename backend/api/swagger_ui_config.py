"""
Swagger UI Configuration
Custom configuration for enhanced Swagger documentation display
"""

# Swagger UI custom CSS for better appearance
SWAGGER_UI_CSS = """
<style>
/* Custom styling for Voxify API documentation */
.swagger-ui .topbar {
    background-color: #1a1a1a;
    border-bottom: 1px solid #3b82f6;
}

.swagger-ui .topbar .link {
    color: #ffffff;
}

.swagger-ui .info {
    margin: 50px 0;
}

.swagger-ui .info .title {
    color: #1f2937;
    font-size: 36px;
    font-weight: bold;
}

.swagger-ui .info .description {
    color: #4b5563;
    font-size: 16px;
    line-height: 1.6;
}

.swagger-ui .scheme-container {
    background: #f9fafb;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.swagger-ui .opblock.opblock-post {
    background: rgba(73, 204, 144, 0.1);
    border-color: #49cc90;
}

.swagger-ui .opblock.opblock-get {
    background: rgba(97, 175, 254, 0.1);
    border-color: #61affe;
}

.swagger-ui .opblock.opblock-put {
    background: rgba(252, 161, 48, 0.1);
    border-color: #fca130;
}

.swagger-ui .opblock.opblock-delete {
    background: rgba(249, 62, 62, 0.1);
    border-color: #f93e3e;
}

.swagger-ui .opblock.opblock-patch {
    background: rgba(80, 227, 194, 0.1);
    border-color: #50e3c2;
}

.swagger-ui .auth-wrapper {
    padding: 20px;
    background: #f8fafc;
    border-radius: 8px;
    margin: 20px 0;
}

.swagger-ui .responses-inner {
    padding: 20px;
    background: #f8fafc;
    border-radius: 8px;
}

/* Custom badges for different API sections */
.swagger-ui .opblock-tag {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    margin: 20px 0 10px 0;
    padding: 10px 0;
    border-bottom: 2px solid #e5e7eb;
}

/* Improve model display */
.swagger-ui .model-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 15px;
}

/* Better code highlighting */
.swagger-ui .highlight-code {
    background: #1f2937;
    color: #f9fafb;
    padding: 15px;
    border-radius: 6px;
    font-family: 'Monaco', 'Consolas', monospace;
}

/* Response status badges */
.swagger-ui .response-col_status {
    font-weight: bold;
}

.swagger-ui .response-col_status .response-undocumented {
    color: #ef4444;
}

/* Parameter styling */
.swagger-ui .parameters-col_description {
    color: #4b5563;
}

.swagger-ui .parameter__name.required {
    color: #dc2626;
    font-weight: bold;
}

.swagger-ui .parameter__name.required:after {
    content: ' *';
    color: #dc2626;
}

/* Security requirements styling */
.swagger-ui .auth-btn-wrapper {
    text-align: center;
    margin: 20px 0;
}

.swagger-ui .authorize {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}

.swagger-ui .authorize:hover {
    background: #2563eb;
}

/* Custom scrollbar */
.swagger-ui ::-webkit-scrollbar {
    width: 8px;
}

.swagger-ui ::-webkit-scrollbar-track {
    background: #f1f5f9;
}

.swagger-ui ::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
}

.swagger-ui ::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .swagger-ui .info .title {
        font-size: 28px;
    }
    
    .swagger-ui .opblock-summary {
        flex-wrap: wrap;
    }
    
    .swagger-ui .opblock-summary-method {
        margin-bottom: 5px;
    }
}
</style>
"""

# Custom JavaScript for enhanced functionality
SWAGGER_UI_JS = """
<script>
// Custom JavaScript for Voxify API documentation
window.addEventListener('DOMContentLoaded', function() {
    // Add custom header with logo and links
    const topbar = document.querySelector('.swagger-ui .topbar');
    if (topbar) {
        const customHeader = document.createElement('div');
        customHeader.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0 20px;">
                <div style="display: flex; align-items: center;">
                    <h2 style="color: white; margin: 0; font-size: 20px;">🎙️ Voxify API</h2>
                    <span style="color: #94a3b8; margin-left: 10px; font-size: 14px;">v1.0.0</span>
                </div>
                <div style="display: flex; gap: 15px;">
                    <a href="https://voxify.app" target="_blank" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Website</a>
                    <a href="mailto:support@voxify.app" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Support</a>
                    <a href="https://github.com/voxify/api" target="_blank" style="color: #94a3b8; text-decoration: none; font-size: 14px;">GitHub</a>
                </div>
            </div>
        `;
        topbar.appendChild(customHeader);
    }

    // Add authentication helper
    const authSection = document.querySelector('.swagger-ui .auth-wrapper');
    if (authSection) {
        const authHelper = document.createElement('div');
        authHelper.innerHTML = `
            <div style="background: #dbeafe; padding: 15px; border-radius: 6px; margin-top: 10px;">
                <h4 style="margin: 0 0 10px 0; color: #1e40af;">🔑 Authentication Helper</h4>
                <p style="margin: 0 0 10px 0; color: #1e40af; font-size: 14px;">
                    To test authenticated endpoints:
                </p>
                <ol style="margin: 0; padding-left: 20px; color: #1e40af; font-size: 14px;">
                    <li>Use the <code>/auth/login</code> endpoint to get an access token</li>
                    <li>Copy the <code>access_token</code> from the response</li>
                    <li>Click the "Authorize" button above</li>
                    <li>Enter: <code>Bearer &lt;your-token&gt;</code></li>
                    <li>Click "Authorize" to save</li>
                </ol>
            </div>
        `;
        authSection.appendChild(authHelper);
    }

    // Add API status indicator
    const info = document.querySelector('.swagger-ui .info');
    if (info) {
        const statusIndicator = document.createElement('div');
        statusIndicator.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px; padding: 15px; background: #d1fae5; border-radius: 8px; margin: 20px 0;">
                <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                <span style="color: #065f46; font-weight: 600;">API Status: Online</span>
                <span style="color: #047857; font-size: 14px;">Last updated: ${new Date().toLocaleString()}</span>
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            </style>
        `;
        info.appendChild(statusIndicator);
    }

    // Add quick navigation
    const schemes = document.querySelector('.swagger-ui .scheme-container');
    if (schemes) {
        const quickNav = document.createElement('div');
        quickNav.innerHTML = `
            <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 15px 0; color: #1f2937;">📋 Quick Navigation</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <a href="#operations-Authentication" style="padding: 10px; background: white; border: 1px solid #e5e7eb; border-radius: 6px; text-decoration: none; color: #374151; font-weight: 500;">🔐 Authentication</a>
                    <a href="#operations-Voice_Management" style="padding: 10px; background: white; border: 1px solid #e5e7eb; border-radius: 6px; text-decoration: none; color: #374151; font-weight: 500;">🎙️ Voice Management</a>
                    <a href="#operations-Job_Management" style="padding: 10px; background: white; border: 1px solid #e5e7eb; border-radius: 6px; text-decoration: none; color: #374151; font-weight: 500;">⚙️ Job Management</a>
                    <a href="#operations-File_Management" style="padding: 10px; background: white; border: 1px solid #e5e7eb; border-radius: 6px; text-decoration: none; color: #374151; font-weight: 500;">📁 File Management</a>
                </div>
            </div>
        `;
        schemes.parentNode.insertBefore(quickNav, schemes.nextSibling);
    }

    // Auto-expand first operation in each section
    setTimeout(() => {
        const tagSections = document.querySelectorAll('.swagger-ui .opblock-tag-section');
        tagSections.forEach(section => {
            const firstOperation = section.querySelector('.opblock');
            if (firstOperation && !firstOperation.classList.contains('is-open')) {
                const summary = firstOperation.querySelector('.opblock-summary');
                if (summary) {
                    summary.click();
                }
            }
        });
    }, 1000);

    // Add copy buttons to code examples
    setTimeout(() => {
        const codeBlocks = document.querySelectorAll('.swagger-ui .highlight-code pre');
        codeBlocks.forEach(block => {
            const copyButton = document.createElement('button');
            copyButton.textContent = 'Copy';
            copyButton.style.cssText = 'position: absolute; top: 10px; right: 10px; background: #3b82f6; color: white; border: none; padding: 5px 10px; border-radius: 4px; font-size: 12px; cursor: pointer;';
            
            const container = block.parentNode;
            container.style.position = 'relative';
            container.appendChild(copyButton);
            
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(block.textContent);
                copyButton.textContent = 'Copied!';
                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                }, 2000);
            });
        });
    }, 1500);
});
</script>
"""

def get_swagger_ui_config():
    """Get Swagger UI configuration with custom styling and functionality"""
    return {
        'docExpansion': 'list',  # Expand operations list by default
        'defaultModelsExpandDepth': 2,  # Expand models
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,  # Show request duration
        'filter': True,  # Enable filtering
        'showExtensions': True,  # Show vendor extensions
        'showCommonExtensions': True,  # Show common extensions
        'tryItOutEnabled': True,  # Enable "Try it out" functionality
        'supportedSubmitMethods': ['get', 'post', 'put', 'delete', 'patch'],
        'validatorUrl': None,  # Disable online validator
        'oauth2RedirectUrl': None,  # OAuth2 redirect URL
        'persistAuthorization': True,  # Remember auth between page reloads
        'layout': 'StandaloneLayout',
        'deepLinking': True,  # Enable deep linking
        'displayOperationId': False,  # Hide operation IDs
        'maxDisplayedTags': 10,  # Maximum number of tags to display
        'operationsSorter': 'alpha',  # Sort operations alphabetically
        'tagsSorter': 'alpha',  # Sort tags alphabetically
        'onComplete': 'customOnComplete',  # Custom completion callback
        'plugins': ['SwaggerUIBundle.plugins.DownloadUrl'],
        'presets': [
            'SwaggerUIBundle.presets.apis',
            'SwaggerUIBundle.presets.standalone'
        ]
    }