import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HelpPage from './HelpPage';

// Mock useNavigate hook
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
}));

// Helper function to render component with router context
const renderWithRouter = (component) => {
    return render(
        <BrowserRouter>
            {component}
        </BrowserRouter>
    );
};

describe('HelpPage', () => {
    beforeEach(() => {
        mockNavigate.mockClear();
    });

    describe('Rendering and Content', () => {
        test('Render main heading correctly', () => {
            renderWithRouter(<HelpPage />);
            const heading = screen.getByRole('heading', { name: /welcome to voxify/i });
            expect(heading).toBeInTheDocument();
            expect(heading).toHaveClass('text-4xl', 'font-bold');
        });

        test('Render all section headings', () => {
            renderWithRouter(<HelpPage />);
            expect(screen.getByRole('heading', { name: /what is voxify\?/i })).toBeInTheDocument();
            expect(screen.getByRole('heading', { name: /using the dashboard/i })).toBeInTheDocument();
            expect(screen.getByRole('heading', { name: /navigation/i })).toBeInTheDocument();
        });

        test('Display Voxify description correctly', () => {
            renderWithRouter(<HelpPage />);
            expect(screen.getByText(/voxify is an ai-powered platform for voice cloning/i)).toBeInTheDocument();
            expect(screen.getByText(/this project focuses on building the core infrastructure/i)).toBeInTheDocument();
        });

        test('Display technology stack information', () => {
            renderWithRouter(<HelpPage />);
            expect(screen.getByText(/python/i)).toBeInTheDocument();
            expect(screen.getByText(/flask/i)).toBeInTheDocument();
            expect(screen.getByText(/sqlite/i)).toBeInTheDocument();
            expect(screen.getByText(/chromadb/i)).toBeInTheDocument();
            expect(screen.getByText(/f5-tts/i)).toBeInTheDocument();
        });

        test('Render dashboard usage instructions', () => {
            renderWithRouter(<HelpPage />);
            expect(screen.getByText(/from your dashboard, you can:/i)).toBeInTheDocument();
            // Test for the key strong elements that represent UI features
            expect(screen.getByText('"Clone Your Voice"')).toBeInTheDocument();
            expect(screen.getByText('"Text-To-Speech"')).toBeInTheDocument();
        });

        test('Render navigation instructions', () => {
            renderWithRouter(<HelpPage />);
            // Test for the key strong elements that represent navigation options
            expect(screen.getByText('"Voices"')).toBeInTheDocument();
            expect(screen.getByText('"Tasks"')).toBeInTheDocument();
            expect(screen.getByText('"View All Tasks"')).toBeInTheDocument();
            expect(screen.getByText('"Settings"')).toBeInTheDocument();
        });
    });

    describe('Button Functionality', () => {
        test('Render both action buttons', () => {
            renderWithRouter(<HelpPage />);
            const dashboardButton = screen.getByRole('button', { name: /go to dashboard/i });
            const cloneButton = screen.getByRole('button', { name: /clone your voice/i });
            expect(dashboardButton).toBeInTheDocument();
            expect(cloneButton).toBeInTheDocument();
        });

        test('Check dashboard button navigates to /dashboard when clicked', () => {
            renderWithRouter(<HelpPage />);
            const dashboardButton = screen.getByRole('button', { name: /go to dashboard/i });
            fireEvent.click(dashboardButton);
            expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
            expect(mockNavigate).toHaveBeenCalledTimes(1);
        });

        test('Clone voice button navigates to /voice-clone when clicked', () => {
            renderWithRouter(<HelpPage />);
            const cloneButton = screen.getByRole('button', { name: /clone your voice/i });
            fireEvent.click(cloneButton);
            expect(mockNavigate).toHaveBeenCalledWith('/voice-clone');
            expect(mockNavigate).toHaveBeenCalledTimes(1);
        });

        test('Check buttons have correct styling classes', () => {
            renderWithRouter(<HelpPage />);
            const dashboardButton = screen.getByRole('button', { name: /go to dashboard/i });
            const cloneButton = screen.getByRole('button', { name: /clone your voice/i });
            expect(dashboardButton).toHaveClass('bg-black', 'text-white', 'px-6', 'py-3', 'rounded-md');
            expect(cloneButton).toHaveClass('bg-black', 'text-white', 'px-6', 'py-3', 'rounded-md');
        });
    });

    describe('Layout and Styling', () => {
        test('Apply correct container classes', () => {
            const { container } = renderWithRouter(<HelpPage />);
            const mainDiv = container.firstChild;
            expect(mainDiv).toHaveClass('min-h-screen', 'bg-black', 'text-white', 'px-4', 'py-12');
        });

        test('Apply correct content wrapper classes', () => {
            renderWithRouter(<HelpPage />);
            const contentWrapper = screen.getByRole('heading', { name: /welcome to voxify/i }).closest('div');
            expect(contentWrapper).toHaveClass('bg-zinc-800', 'rounded-xl', 'shadow-lg', 'p-8', 'space-y-6');
        });

        test('Button container has correct styling', () => {
            renderWithRouter(<HelpPage />);
            const buttonContainer = screen.getByRole('button', { name: /go to dashboard/i }).parentElement;
            expect(buttonContainer).toHaveClass('pt-6', 'flex', 'justify-center', 'gap-4');
        });
    });

    describe('Accessibility', () => {
        test('Check proper heading hierarchy', () => {
            renderWithRouter(<HelpPage />);
            const h1 = screen.getByRole('heading', { level: 1 });
            const h2Elements = screen.getAllByRole('heading', { level: 2 });
            expect(h1).toBeInTheDocument();
            expect(h2Elements).toHaveLength(3);
        });

        test('Check buttons are accessible via keyboard', () => {
            renderWithRouter(<HelpPage />);
            const dashboardButton = screen.getByRole('button', { name: /go to dashboard/i });
            const cloneButton = screen.getByRole('button', { name: /clone your voice/i });
            // Focus the buttons
            dashboardButton.focus();
            expect(document.activeElement).toBe(dashboardButton);
            cloneButton.focus();
            expect(document.activeElement).toBe(cloneButton);
        });

        test('Check lists are properly structured', () => {
            renderWithRouter(<HelpPage />);
            const lists = screen.getAllByRole('list');
            expect(lists).toHaveLength(2);
            const listItems = screen.getAllByRole('listitem');
            expect(listItems.length).toBeGreaterThan(0);
        });
    });

    describe('Content Structure', () => {
        test('Check sections are properly organized', () => {
            renderWithRouter(<HelpPage />);
            const sections = screen.getAllByRole('heading', { level: 2 });
            const expectedSections = ['What is Voxify?', 'Using the Dashboard', 'Navigation'];
            sections.forEach((section, index) => {
                expect(section).toHaveTextContent(expectedSections[index]);
            });
        });

        test('Check strong text elements are present for emphasis', () => {
            renderWithRouter(<HelpPage />);
            const strongElements = screen.getAllByText((content, element) => {
                return element?.tagName.toLowerCase() === 'strong';
            });
            expect(strongElements.length).toBeGreaterThan(0);
        });
    });

    describe('Error Boundaries and Edge Cases', () => {
        test('Handle multiple rapid button clicks', () => {
            renderWithRouter(<HelpPage />);
            const dashboardButton = screen.getByRole('button', { name: /go to dashboard/i });
            // Simulate rapid clicks
            fireEvent.click(dashboardButton);
            fireEvent.click(dashboardButton);
            fireEvent.click(dashboardButton);
            expect(mockNavigate).toHaveBeenCalledTimes(3);
            expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
        });

        test('Render without crashing when navigation is unavailable', () => {
            expect(() => {
                renderWithRouter(<HelpPage />);
            }).not.toThrow();
        });
    });
});
