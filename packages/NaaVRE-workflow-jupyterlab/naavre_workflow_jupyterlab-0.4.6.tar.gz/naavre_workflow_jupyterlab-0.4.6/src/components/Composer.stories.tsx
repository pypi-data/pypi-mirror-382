import type { Meta, StoryObj } from '@storybook/react-webpack5';

import { Composer } from './Composer';

const meta = {
  component: Composer
} satisfies Meta<typeof Composer>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
