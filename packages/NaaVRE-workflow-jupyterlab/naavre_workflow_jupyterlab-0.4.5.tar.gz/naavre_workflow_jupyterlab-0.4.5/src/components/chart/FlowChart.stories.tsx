import React, { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-webpack5';
import { mapValues } from 'lodash';
import {
  actions,
  FlowChart,
  IChart,
  INodeDefaultProps
} from '@mrblenny/react-flow-chart';

import { chart as mockChart } from '../../mocks/chart';
import { NodeCustom } from './NodeCustom';
import { NodeInnerCustom } from './NodeInnerCustom';
import { PortCustom } from './PortCustom';
import { LinkCustom } from './LinkCustom';
import { validateLink } from '../../utils/chart';

function FlowChartStory() {
  const [chart, setChart] = useState<IChart>(mockChart);
  const chartStateActions = mapValues(
    actions,
    (func: any) =>
      (...args: any) => {
        const newChartTransformer = func(...args);
        const newChart = newChartTransformer(chart);
        setChart(chart => ({ ...chart, ...newChart }));
      }
  ) as typeof actions;
  return (
    <FlowChart
      chart={chart}
      callbacks={chartStateActions}
      config={{
        readonly: false,
        validateLink: validateLink
      }}
      Components={{
        Node: NodeCustom as React.FunctionComponent<INodeDefaultProps>,
        NodeInner: NodeInnerCustom,
        Port: PortCustom,
        Link: LinkCustom
      }}
    />
  );
}

const meta = {
  component: FlowChartStory
} satisfies Meta<typeof FlowChart>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
