import { ISharingScope } from '../../naavre-common/types/NaaVRECatalogue/BaseAssets';
import { INaaVREExternalServiceResponse } from '../../naavre-common/handler';

export const sharingScopes: ISharingScope[] = [
  {
    url: 'http://localhost:56848/sharing-scopes/test-community-1/',
    title: 'Test Community 1',
    label: 'community',
    show_in_virtual_labs: ['test-virtual-lab-1', 'test-virtual-lab-2'],
    check_in_virtual_labs: ['test-virtual-lab-1', 'test-virtual-lab-2']
  },
  {
    url: 'http://localhost:56848/sharing-scopes/test-community-1/',
    title: 'Test Community 2',
    label: 'community',
    show_in_virtual_labs: ['test-virtual-lab-2'],
    check_in_virtual_labs: ['test-virtual-lab-2']
  },
  {
    url: 'http://localhost:56848/sharing-scopes/test-virtual-lab-1/',
    title: 'Test Virtual Lab 1',
    label: 'virtual_lab',
    show_in_virtual_labs: ['test-virtual-lab-1', 'test-virtual-lab-2'],
    check_in_virtual_labs: ['test-virtual-lab-1']
  },
  {
    url: 'http://localhost:56848/sharing-scopes/test-virtual-lab-2/',
    title: 'Test Virtual Lab 2',
    label: 'virtual_lab',
    show_in_virtual_labs: ['test-virtual-lab-1', 'test-virtual-lab-2'],
    check_in_virtual_labs: ['test-virtual-lab-2']
  }
];

export async function getSharingScopesList(
  request: Request
): Promise<INaaVREExternalServiceResponse> {
  return {
    status_code: 200,
    reason: 'OK',
    headers: {
      'content-type': 'application/json'
    },
    content: JSON.stringify({
      count: sharingScopes.length,
      next: null,
      previous: null,
      results: sharingScopes
    })
  };
}
