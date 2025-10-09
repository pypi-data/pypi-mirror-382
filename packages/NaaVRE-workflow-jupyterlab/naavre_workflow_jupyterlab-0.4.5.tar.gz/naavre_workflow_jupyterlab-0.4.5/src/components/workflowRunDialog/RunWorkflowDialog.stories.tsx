import type { Meta, StoryObj } from '@storybook/react-webpack5';

import { chart as mockChart } from '../../mocks/chart';
import { RunWorkflowDialog } from './RunWorkflowDialog';

const meta = {
  component: RunWorkflowDialog
} satisfies Meta<typeof RunWorkflowDialog>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    chart: mockChart
  }
};
