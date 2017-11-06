#
# Copyright (c) 2017 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 3 (GPLv3). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv3
# along with this software; if not, see
# https://www.gnu.org/licenses/gpl-3.0.txt.
#
"""Test the API application."""

import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from api.models import HostCredential


class HostCredentialTest(TestCase):
    """Tests against the HostCredential model and view set."""

    # pylint: disable= no-self-use
    def create_hostcredential(self, name='test_cred',
                              username='testuser', password='testpass'):
        """Create a HostCredential model for use within test cases.

        :param name: name of the host credential
        :param username: the user used during the discovery and inspection
        :param password: the connection password
        :returns: A HostCredential model
        """
        return HostCredential.objects.create(name=name,
                                             username=username,
                                             password=password)

    def test_hostcred_creation(self):
        """Tests the creation of a HostCredential model."""
        host_cred = self.create_hostcredential()
        self.assertTrue(isinstance(host_cred, HostCredential))

    def test_hostcred_create(self):
        """Ensure we can create a new host credential object via API."""
        url = reverse('hostcred-list')
        data = {'name': 'cred1',
                'username': 'user1',
                'password': 'pass1'}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HostCredential.objects.count(), 1)
        self.assertEqual(HostCredential.objects.get().name, 'cred1')

    def test_hc_create_err_name(self):
        """Test create without name.

        Ensure we cannot create a new host credential object without a name.
        """
        expected_error = {'name': ['This field is required.']}
        url = reverse('hostcred-list')
        data = {'username': 'user1',
                'password': 'pass1'}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hc_create_err_username(self):
        """Test create without username.

        Ensure we cannot create a new host credential object without a
        username.
        """
        expected_error = {'username': ['This field is required.']}
        url = reverse('hostcred-list')
        data = {'name': 'cred1',
                'password': 'pass1'}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hc_create_err_p_or_ssh(self):
        """Test API without password or keyfile.

        Ensure we cannot create a new host credential object without a password
        or an ssh_keyfile.
        """
        expected_error = {'non_field_errors': ['A host credential must have '
                                               'either a password or an '
                                               'ssh_keyfile.']}
        url = reverse('hostcred-list')
        data = {'name': 'cred1',
                'username': 'user1'}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hc_create_err_ssh_bad(self):
        """Test API with bad sshkey.

        Ensure we cannot create a new host credential object an ssh_keyfile
        that cannot be found on the server.
        """
        expected_error = {'non_field_errors': ['ssh_keyfile, blah, is not a '
                                               'valid file on the system.']}
        url = reverse('hostcred-list')
        data = {'name': 'cred1',
                'username': 'user1',
                'ssh_keyfile': 'blah'}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hc_create_long_name(self):
        """Test API with long name.

        Ensure we cannot create a new host credential object with a
        long name.
        """
        expected_error = {'name': ['Ensure this field has no more than '
                                   '64 characters.']}
        url = reverse('hostcred-list')
        data = {'name': 'A' * 100,
                'username': 'user1',
                'password': 'pass1'}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hc_create_long_user(self):
        """Test API with long user.

        Ensure we cannot create a new host credential object with a
        long username.
        """
        expected_error = {'username': ['Ensure this field has no more than '
                                       '64 characters.']}
        url = reverse('hostcred-list')
        data = {'name': 'cred1',
                'username': 'A' * 100,
                'password': 'pass1'}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hc_create_long_password(self):
        """Test api with long password.

        Ensure we cannot create a new host credential object with a
        long password.
        """
        expected_error = {'password': ['Ensure this field has no more than '
                                       '1024 characters.']}
        url = reverse('hostcred-list')
        data = {'name': 'cred1',
                'username': 'user1',
                'password': 'A' * 2000}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hc_create_long_sudo(self):
        """Test api with long sudo.

        Ensure we cannot create a new host credential object with a
        long sudo_password.
        """
        expected_error = {'sudo_password': ['Ensure this field has no more '
                                            'than 1024 characters.']}
        url = reverse('hostcred-list')
        data = {'name': 'cred1',
                'username': 'user1',
                'password': 'pass1',
                'sudo_password': 'A' * 2000}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hc_create_long_ssh(self):
        """Test api with long ssh.

        Ensure we cannot create a new host credential object with a
        long ssh_keyfile.
        """
        expected_error = {'ssh_keyfile': ['Ensure this field has no more than '
                                          '1024 characters.']}
        url = reverse('hostcred-list')
        data = {'name': 'cred1',
                'username': 'user1',
                'ssh_keyfile': 'A' * 2000}
        response = self.client.post(url, json.dumps(data),
                                    'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_error)

    def test_hostcred_list_view(self):
        """Tests the list view set of the HostCredential API."""
        url = reverse('hostcred-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_hostcred_update_view(self):
        """Tests the update view set of the HostCredential API."""
        cred = HostCredential(name='cred2', username='user2',
                              password='pass2')
        cred.save()
        data = {'name': 'cred2',
                'username': 'user2',
                'password': 'pass3'}
        url = reverse('hostcred-detail', args=(cred.pk,))
        resp = self.client.put(url, json.dumps(data),
                               content_type='application/json',
                               format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_hostcred_delete_view(self):
        """Tests the delete view set of the HostCredential API."""
        cred = HostCredential(name='cred2', username='user2',
                              password='pass2')
        cred.save()
        url = reverse('hostcred-detail', args=(cred.pk,))
        resp = self.client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)