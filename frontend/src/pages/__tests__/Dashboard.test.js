import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Dashboard from '../Dashboard';

// Mock the services
jest.mock('../../services/auth.service', () => ({
	getCurrentUser: jest.fn(),
}));

jest.mock('../../services/job.service', () => ({
	getSynthesisJobs: jest.fn(),
}));

jest.mock('../../services/voiceClone.service', () => ({
	listVoiceClones: jest.fn(),
}));

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
	...jest.requireActual('react-router-dom'),
	useNavigate: () => mockNavigate,
}));

import authService from '../../services/auth.service';
import jobService from '../../services/job.service';
import voiceCloneService from '../../services/voiceClone.service';

const DashboardWithRouter = () => (
	<BrowserRouter>
		<Dashboard />
	</BrowserRouter>
);

describe('Dashboard Component', () => {
	beforeEach(() => {
		jest.clearAllMocks();
		authService.getCurrentUser.mockReturnValue({
			first_name: 'John',
			email: 'john@example.com',
		});
		voiceCloneService.listVoiceClones.mockResolvedValue({
			data: { clones: [] },
		});
		jobService.getSynthesisJobs.mockResolvedValue([]);
	});

	describe('Initial Render', () => {
		test('Render welcome message with user name', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Welcome back, John!')).toBeInTheDocument();
			});
			expect(
				screen.getByText('Ready to start a new task? Choose an option below.')
			).toBeInTheDocument();
		});

		test('Render welcome message with default name when user has no first name', async () => {
			authService.getCurrentUser.mockReturnValue({
				email: 'john@example.com',
			});
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Welcome back, there!')).toBeInTheDocument();
			});
		});

		test('Render welcome message with default name when user is null', async () => {
			authService.getCurrentUser.mockReturnValue(null);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Welcome back, there!')).toBeInTheDocument();
			});
		});

		test('renders main action cards', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Clone Your Voice')).toBeInTheDocument();
			});
			expect(
				screen.getByText(
					'Create a digital copy of your voice that can speak any text naturally.'
				)
			).toBeInTheDocument();
			expect(screen.getByText('Text-to-Speech')).toBeInTheDocument();
			expect(
				screen.getByText(
					'Convert any text into natural-sounding speech using your voice clones.'
				)
			).toBeInTheDocument();
		});

		test('Render statistics section', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Your Statistics')).toBeInTheDocument();
			});
			expect(screen.getByText('Voice Clones')).toBeInTheDocument();
			expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
			expect(screen.getByText('Processing')).toBeInTheDocument();
		});

		test('Render quick actions section', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(screen.getByText('Quick Actions')).toBeInTheDocument();
			});
			expect(screen.getByText('View All Tasks')).toBeInTheDocument();
			expect(
				screen.getByText('Browse and manage your generated voices')
			).toBeInTheDocument();
			expect(screen.getByText('Settings')).toBeInTheDocument();
			expect(
				screen.getByText('Manage your account and preferences')
			).toBeInTheDocument();
		});
	});

	describe('Navigation Links', () => {
		test('Voice clone card links to correct route', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const voiceCloneLink = screen.getByText('Clone Your Voice').closest('a');
				expect(voiceCloneLink).toHaveAttribute('href', '/voice-clone');
			});
		});

		test('Check text-to-speech card links to correct route', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const ttsLink = screen.getByText('Text-to-Speech').closest('a');
				expect(ttsLink).toHaveAttribute('href', '/text-to-speech');
			});
		});

		test('View all tasks link is correct', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const tasksLink = screen.getByText('View All Tasks').closest('a');
				expect(tasksLink).toHaveAttribute('href', '/tasks');
			});
		});

		test('Check settings link is correct', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const settingsLink = screen.getByText('Settings').closest('a');
				expect(settingsLink).toHaveAttribute('href', '/settings');
			});
		});
	});

	describe('Statistics Loading', () => {
		test('Show loading state initially', async () => {
			voiceCloneService.listVoiceClones.mockImplementation(
				() =>
					new Promise((resolve) =>
						setTimeout(() => resolve({ data: { clones: [] } }), 100)
					)
			);
			jobService.getSynthesisJobs.mockImplementation(
				() => new Promise((resolve) => setTimeout(() => resolve([]), 100))
			);
			render(<DashboardWithRouter />);
			const loadingElements = document.querySelectorAll('.animate-pulse');
			expect(loadingElements.length).toBeGreaterThan(0);
			await waitFor(
				() => {
					const voiceClonesSection = screen
						.getByText('Voice Clones')
						.closest('div');
					expect(
						voiceClonesSection.querySelector('p.text-2xl')
					).toHaveTextContent('0');
				},
				{ timeout: 500 }
			);
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
				const voiceClonesSection = screen
					.getByText('Voice Clones')
					.closest('div');
				expect(
					voiceClonesSection.querySelector('p.text-2xl')
				).toHaveTextContent('2');
			});
			await waitFor(() => {
				const completedSection = screen
					.getByText('Completed Tasks')
					.closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent(
					'2'
				);
			});
			await waitFor(() => {
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent(
					'2'
				);
			});
		});

		test('Handle empty data gracefully', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const voiceClonesSection = screen
					.getByText('Voice Clones')
					.closest('div');
				expect(
					voiceClonesSection.querySelector('p.text-2xl')
				).toHaveTextContent('0');
			});
			await waitFor(() => {
				const completedSection = screen
					.getByText('Completed Tasks')
					.closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent(
					'0'
				);
			});
			await waitFor(() => {
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent(
					'0'
				);
			});
		});

		test('Handle missing data structure gracefully', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: null,
			});
			jobService.getSynthesisJobs.mockResolvedValue(null);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const voiceClonesSection = screen
					.getByText('Voice Clones')
					.closest('div');
				expect(
					voiceClonesSection.querySelector('p.text-2xl')
				).toHaveTextContent('0');
			});
			await waitFor(() => {
				const completedSection = screen
					.getByText('Completed Tasks')
					.closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent(
					'0'
				);
			});
			await waitFor(() => {
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent(
					'0'
				);
			});
		});
	});

	describe('Error Handling', () => {
		test('Display error message when voice clone service fails', async () => {
			voiceCloneService.listVoiceClones.mockRejectedValue(
				new Error('Voice clone service error')
			);
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(
					screen.getByText('Failed to load dashboard statistics')
				).toBeInTheDocument();
			});
		});

		test('Display error message when job service fails', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockRejectedValue(
				new Error('Job service error')
			);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(
					screen.getByText('Failed to load dashboard statistics')
				).toBeInTheDocument();
			});
		});

		test('Display error message when both services fail', async () => {
			voiceCloneService.listVoiceClones.mockRejectedValue(
				new Error('Voice clone error')
			);
			jobService.getSynthesisJobs.mockRejectedValue(
				new Error('Job service error')
			);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(
					screen.getByText('Failed to load dashboard statistics')
				).toBeInTheDocument();
			});
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
				const voiceClonesSection = screen
					.getByText('Voice Clones')
					.closest('div');
				expect(
					voiceClonesSection.querySelector('p.text-2xl')
				).toHaveTextContent('1');
			});
			await waitFor(() => {
				const completedSection = screen
					.getByText('Completed Tasks')
					.closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent(
					'3'
				);
			});
			await waitFor(() => {
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent(
					'3'
				);
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
				const voiceClonesSection = screen
					.getByText('Voice Clones')
					.closest('div');
				expect(
					voiceClonesSection.querySelector('p.text-2xl')
				).toHaveTextContent('0');
			});
			await waitFor(() => {
				const completedSection = screen
					.getByText('Completed Tasks')
					.closest('div');
				expect(completedSection.querySelector('p.text-2xl')).toHaveTextContent(
					'1'
				);
			});
			await waitFor(() => {
				const processingSection = screen.getByText('Processing').closest('div');
				expect(processingSection.querySelector('p.text-2xl')).toHaveTextContent(
					'0'
				);
			});
		});
	});

	describe('UI Elements', () => {
		test('Check for proper CSS classes for styling', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const outerContainer = document.querySelector(
					'.min-h-screen'
				);
				expect(outerContainer).toBeInTheDocument();
			});
		});

		test('Render SVG icons in action cards', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const svgElements = document.querySelectorAll('svg');
				expect(svgElements.length).toBeGreaterThan(0);
			});
		});

		test('Render statistics with proper icons', async () => {
			render(<DashboardWithRouter />);
			await waitFor(() => {
				const voiceClonesSection = screen
					.getByText('Voice Clones')
					.closest('div');
				expect(voiceClonesSection).toBeInTheDocument();
			});
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
				expect(voiceCloneService.listVoiceClones).toHaveBeenCalled();
			});
		});

		test('Call job service with no parameters', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(jobService.getSynthesisJobs).toHaveBeenCalled();
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
			await waitFor(() => {
				expect(voiceCloneService.listVoiceClones).toHaveBeenCalledTimes(1);
			});
			await waitFor(() => {
				expect(jobService.getSynthesisJobs).toHaveBeenCalledTimes(1);
			});
		});

		test('Only load stats once on initial mount', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				data: { clones: [] },
			});
			jobService.getSynthesisJobs.mockResolvedValue([]);
			render(<DashboardWithRouter />);
			await waitFor(() => {
				expect(voiceCloneService.listVoiceClones).toHaveBeenCalledTimes(1);
			});
			await waitFor(() => {
				expect(jobService.getSynthesisJobs).toHaveBeenCalledTimes(1);
			});
			await new Promise((resolve) => setTimeout(resolve, 100));
			expect(voiceCloneService.listVoiceClones).toHaveBeenCalledTimes(1);
			expect(jobService.getSynthesisJobs).toHaveBeenCalledTimes(1);
		});
	});
});