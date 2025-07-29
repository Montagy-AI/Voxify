import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Dashboard from './Dashboard';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
	...jest.requireActual('react-router-dom'),
	useNavigate: () => mockNavigate,
}));

// Mock the services
jest.mock('../services/auth.service', () => ({
	getCurrentUser: jest.fn(),
}));

jest.mock('../services/job.service', () => ({
	getSynthesisJobs: jest.fn(),
}));

jest.mock('../services/voiceClone.service', () => ({
	listVoiceClones: jest.fn(),
}));

// Import mocked services
import authService from '../services/auth.service';
import jobService from '../services/job.service';
import voiceCloneService from '../services/voiceClone.service';

// Helper component to wrap Dashboard with Router
const DashboardWithRouter = () => (
	<BrowserRouter>
		<Dashboard />
	</BrowserRouter>
);

describe('Dashboard Component', () => {
	beforeEach(() => {
		jest.clearAllMocks();
		// Default user mock
		authService.getCurrentUser.mockReturnValue({
			first_name: 'John',
			email: 'john@example.com',
		});
	});

	describe('Initial Render', () => {
		test('Render welcome message with user name', () => {
			render(<DashboardWithRouter />);
			expect(screen.getByText('Welcome back, John!')).toBeInTheDocument();
			expect(screen.getByText('Ready to start a new task? Choose an option below.')).toBeInTheDocument();
		});

		test('Render welcome message with default name when user has no first name', () => {
			authService.getCurrentUser.mockReturnValue({
				email: 'john@example.com',
			});
			render(<DashboardWithRouter />);
			expect(screen.getByText('Welcome back, there!')).toBeInTheDocument();
		});

		test('Render welcome message with default name when user is null', () => {
			authService.getCurrentUser.mockReturnValue(null);
			render(<DashboardWithRouter />);
			expect(screen.getByText('Welcome back, there!')).toBeInTheDocument();
		});

		test('renders main action cards', () => {
			render(<DashboardWithRouter />);
			expect(screen.getByText('Clone Your Voice')).toBeInTheDocument();
			expect(screen.getByText(
                'Create a digital copy of your voice that can speak any text naturally.'
            )).toBeInTheDocument();
			expect(screen.getByText('Text-to-Speech')).toBeInTheDocument();
			expect(screen.getByText(
                'Convert any text into natural-sounding speech using your voice clones.'
            )).toBeInTheDocument();
		});

		test('Render statistics section', () => {
			render(<DashboardWithRouter />);
			expect(screen.getByText('Your Statistics')).toBeInTheDocument();
			expect(screen.getByText('Voice Clones')).toBeInTheDocument();
			expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
			expect(screen.getByText('Processing')).toBeInTheDocument();
		});

		test('Render quick actions section', () => {
			render(<DashboardWithRouter />);
			expect(screen.getByText('Quick Actions')).toBeInTheDocument();
			expect(screen.getByText('View All Tasks')).toBeInTheDocument();
			expect(screen.getByText('Browse and manage your generated voices')).toBeInTheDocument();
			expect(screen.getByText('Settings')).toBeInTheDocument();
			expect(screen.getByText('Manage your account and preferences')).toBeInTheDocument();
		});
	});

	describe('Navigation Links', () => {
		test('Voice clone card links to correct route', () => {
			render(<DashboardWithRouter />);
			const voiceCloneLink = screen.getByText('Clone Your Voice').closest('a');
			expect(voiceCloneLink).toHaveAttribute('href', '/voice-clone');
		});

		test('Check text-to-speech card links to correct route', () => {
			render(<DashboardWithRouter />);
			const ttsLink = screen.getByText('Text-to-Speech').closest('a');
			expect(ttsLink).toHaveAttribute('href', '/text-to-speech');
		});

		test('View all tasks link is correct', () => {
			render(<DashboardWithRouter />);
			const tasksLink = screen.getByText('View All Tasks').closest('a');
			expect(tasksLink).toHaveAttribute('href', '/tasks');
		});

		test('Check settings link is correct', () => {
			render(<DashboardWithRouter />);
			const settingsLink = screen.getByText('Settings').closest('a');
			expect(settingsLink).toHaveAttribute('href', '/settings');
		});
	});

	describe('Statistics Loading', () => {
		test('Show loading state initially', async () => {
			// Mock slow API responses
			voiceCloneService.listVoiceClones.mockImplementation(() => 
				new Promise(resolve => setTimeout(() => resolve({ data: { clones: [] } }), 100))
			);
			jobService.getSynthesisJobs.mockImplementation(() => 
				new Promise(resolve => setTimeout(() => resolve([]), 100))
			);
			render(<DashboardWithRouter />);
			// Check for loading animations
			const loadingElements = document.querySelectorAll('.animate-pulse');
			expect(loadingElements.length).toBeGreaterThan(0);
			// Check that data has loaded
			await waitFor(() => {
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			}, { timeout: 500 });
		});

		test('Load and displays statistics successfully', async () => {
			const mockVoiceClones = [
				{ id: 1, name: 'Voice 1' },
				{ id: 2, name: 'Voice 2' },
			];

			const mockJobs = [
				{ id: 1, status: 'completed' },
				{ id: 2, status: 'completed' },
				{ id: 3, status: 'processing' },
				{ id: 4, status: 'pending' },
			];

			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: mockVoiceClones },
			});
			jobService.getSynthesisJobs.mockResolvedValue(mockJobs);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				// Check voice clones count by finding it in the Voice Clones section
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('2');
			});
			await waitFor(() => {
				// Check completed tasks count by finding it in the Completed Tasks section
				const completedSection = screen.getByText('Completed Tasks').closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent('2');
			});
			await waitFor(() => {
				// Check processing tasks count by finding it in the Processing section
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent('2');
			});
		});

		test('Handle empty data gracefully', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
			await waitFor(() => {
				const completedSection = screen.getByText('Completed Tasks').closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
			await waitFor(() => {
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
		});

		test('Handle missing data structure gracefully', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: null,
			});
			jobService.getSynthesisJobs.mockResolvedValue(null);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
			await waitFor(() => {
				const completedSection = screen.getByText('Completed Tasks').closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
			await waitFor(() => {
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
		});
	});

	describe('Error Handling', () => {
		test('Display error message when voice clone service fails', async () => {
			voiceCloneService.listVoiceClones.mockRejectedValue(new Error('Voice clone service error'));
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Failed to load dashboard statistics')).toBeInTheDocument();
			});
			// Should show default stats (zeros) in each section
			await waitFor(() => {
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
		});

		test('Display error message when job service fails', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({ data: { clones: [] } });
			jobService.getSynthesisJobs.mockRejectedValue(new Error('Job service error'));
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Failed to load dashboard statistics')).toBeInTheDocument();
			});
			// Should show default stats (zeros)
			await waitFor(() => {
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
		});

		test('Display error message when both services fail', async () => {
			voiceCloneService.listVoiceClones.mockRejectedValue(new Error('Voice clone error'));
			jobService.getSynthesisJobs.mockRejectedValue(new Error('Job service error'));
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Failed to load dashboard statistics')).toBeInTheDocument();
			});
			await waitFor(() => {
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
		});

		test('Log error to console when loading fails', async () => {
			const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
			voiceCloneService.listVoiceClones.mockRejectedValue(new Error('Test error'));
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(consoleSpy).toHaveBeenCalledWith('Failed to load dashboard stats:', expect.any(Error));
			});
			consoleSpy.mockRestore();
		});
	});

	describe('Statistics Calculations', () => {
		test('Correctly count different job statuses', async () => {
			const mockJobs = [
				{ id: 1, status: 'completed' },
				{ id: 2, status: 'completed' },
				{ id: 3, status: 'completed' },
				{ id: 4, status: 'processing' },
				{ id: 5, status: 'processing' },
				{ id: 6, status: 'pending' },
				{ id: 7, status: 'failed' },
				{ id: 8, status: 'cancelled' },
			];
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [{ id: 1 }] },
			});
			jobService.getSynthesisJobs.mockResolvedValue(mockJobs);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				// Check voice clones count
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('1');
			});
			await waitFor(() => {
				// Check completed tasks count
				const completedSection = screen.getByText('Completed Tasks').closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent('3');
			});
			await waitFor(() => {
				// Check processing tasks count (processing + pending)
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent('3');
			});
		});

		test('Handle jobs with unknown statuses', async () => {
			const mockJobs = [
				{ id: 1, status: 'completed' },
				{ id: 2, status: 'some_unknown_status' },
				{ id: 3, status: null },
				{ id: 4, status: undefined },
			];
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue(mockJobs);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				// Check voice clones count
				const voiceClonesSection = screen.getByText('Voice Clones').closest('div');
				expect(voiceClonesSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
			await waitFor(() => {
				// Should only count the completed job
				const completedSection = screen.getByText('Completed Tasks').closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent('1');
			});
			await waitFor(() => {
				// No processing tasks
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent('0');
			});
		});
	});

	describe('UI Elements', () => {
		test('Check for proper CSS classes for styling', () => {
			render(<DashboardWithRouter />);
			// Find the outermost container with the styling classes
			const outerContainer = document.querySelector('.min-h-screen.bg-black.text-white.p-8');
			expect(outerContainer).toBeInTheDocument();
		});

		test('Render SVG icons in action cards', () => {
			render(<DashboardWithRouter />);
			// Check for SVG elements (arrows in action cards)
			const svgElements = document.querySelectorAll('svg');
			expect(svgElements.length).toBeGreaterThan(0);
		});

		test('Render statistics with proper icons', () => {
			render(<DashboardWithRouter />);
			// Voice Clones
			const voiceClonesSection = screen.getByText('Voice Clones').closest('.bg-zinc-900');
			expect(voiceClonesSection.querySelector('svg')).toBeInTheDocument();
			// Completed Tasks
			const completedSection = screen.getByText('Completed Tasks').closest('.bg-zinc-900');
			expect(completedSection.querySelector('svg')).toBeInTheDocument();
			// CProcessing
			const processingSection = screen.getByText('Processing').closest('.bg-zinc-900');
			expect(processingSection.querySelector('svg')).toBeInTheDocument();
		});
	});

	describe('Service Call Parameters', () => {
		test('Call voice clone service with correct parameters', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(voiceCloneService.listVoiceClones).toHaveBeenCalledWith(1, 100);
			});
		});

		test('Call job service with no parameters', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(jobService.getSynthesisJobs).toHaveBeenCalledWith();
			});
		});
	});

	describe('Component Lifecycle', () => {
		test('Load dashboard stats on mount', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			// Wait for the calls to complete
			await waitFor(() => {
				expect(voiceCloneService.listVoiceClones).toHaveBeenCalledTimes(1);
				expect(jobService.getSynthesisJobs).toHaveBeenCalledTimes(1);
			});
		});

		test('Only load stats once on initial mount', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			// Wait for initial calls
			await waitFor(() => {
				expect(voiceCloneService.listVoiceClones).toHaveBeenCalledTimes(1);
				expect(jobService.getSynthesisJobs).toHaveBeenCalledTimes(1);
			});
			await new Promise(resolve => setTimeout(resolve, 100));
			// Should only be called once
			expect(voiceCloneService.listVoiceClones).toHaveBeenCalledTimes(1);
			expect(jobService.getSynthesisJobs).toHaveBeenCalledTimes(1);
		});
	});
});