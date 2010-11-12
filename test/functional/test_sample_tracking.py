import galaxy.model
from galaxy.model.orm import *
from base.twilltestcase import *
from base.test_db_util import *

sample_states = [  ( 'New', 'Sample entered into the system' ), 
                   ( 'Received', 'Sample tube received' ),
                   ( 'Library Started', 'Sample library preparation' ), 
                   ( 'Run Started', 'Sequence run in progress' ), 
                   ( 'Done', 'Sequence run complete' ) ]
address_dict = dict( short_desc="Office",
                     name="James Bond",
                     institution="MI6" ,
                     address="MI6 Headquarters",
                     city="London",
                     state="London",
                     postal_code="007",
                     country="United Kingdom",
                     phone="007-007-0007" )

class TestFormsAndRequests( TwillTestCase ):
    #
    # ====== Setup Users, Groups & Roles required for this test suite ========= 
    #
    def test_000_initiate_users( self ):
        """Ensuring all required user accounts exist"""
        self.logout()
        self.login( email='test1@bx.psu.edu', username='regular-user1' )
        global regular_user1
        regular_user1 = get_user( 'test1@bx.psu.edu' )
        assert regular_user1 is not None, 'Problem retrieving user with email "test1@bx.psu.edu" from the database'
        global regular_user1_private_role
        regular_user1_private_role = get_private_role( regular_user1 )
        self.logout()
        self.login( email='test2@bx.psu.edu', username='regular-user2' )
        global regular_user2
        regular_user2 = get_user( 'test2@bx.psu.edu' )
        assert regular_user2 is not None, 'Problem retrieving user with email "test2@bx.psu.edu" from the database'
        global regular_user2_private_role
        regular_user2_private_role = get_private_role( regular_user2 )
        self.logout()
        self.login( email='test3@bx.psu.edu', username='regular-user3' )
        global regular_user3
        regular_user3 = get_user( 'test3@bx.psu.edu' )
        assert regular_user3 is not None, 'Problem retrieving user with email "test3@bx.psu.edu" from the database'
        global regular_user3_private_role
        regular_user3_private_role = get_private_role( regular_user3 )
        self.logout()
        self.login( email='test@bx.psu.edu', username='admin-user' )
        global admin_user
        admin_user = get_user( 'test@bx.psu.edu' )
        assert admin_user is not None, 'Problem retrieving user with email "test@bx.psu.edu" from the database'
        global admin_user_private_role
        admin_user_private_role = get_private_role( admin_user )
    def test_005_create_required_groups_and_roles( self ):
        """Testing creating all required groups and roles for this script"""
        # Logged in as admin_user
        # Create role1
        name = 'Role1'
        description = "This is Role1's description"
        user_ids = [ str( admin_user.id ), str( regular_user1.id ), str( regular_user3.id ) ]
        self.create_role( name=name,
                          description=description,
                          in_user_ids=user_ids,
                          in_group_ids=[],
                          create_group_for_role='no',
                          private_role=admin_user.email )
        # Get the role object for later tests
        global role1
        role1 = get_role_by_name( name )
        # Create group1
        name = 'Group1'
        self.create_group( name=name, in_user_ids=[ str( regular_user1.id ) ], in_role_ids=[ str( role1.id ) ] )
        # Get the group object for later tests
        global group1
        group1 = get_group_by_name( name )
        assert group1 is not None, 'Problem retrieving group named "Group1" from the database'
        # NOTE: To get this to work with twill, all select lists on the ~/admin/role page must contain at least
        # 1 option value or twill throws an exception, which is: ParseError: OPTION outside of SELECT
        # Due to this bug in twill, we create the role, we bypass the page and visit the URL in the
        # associate_users_and_groups_with_role() method.
        #
        #create role2
        name = 'Role2'
        description = 'This is Role2'
        user_ids = [ str( admin_user.id ) ]
        group_ids = [ str( group1.id ) ]
        private_role = admin_user.email
        self.create_role( name=name,
                          description=description,
                          in_user_ids=user_ids,
                          in_group_ids=group_ids,
                          private_role=private_role )
        # Get the role object for later tests
        global role2
        role2 = get_role_by_name( name )
        assert role2 is not None, 'Problem retrieving role named "Role2" from the database'
    def test_006_create_library_and_folder( self ):
        """Testing creating the target data library and folder"""
        # Logged in as admin_user
        for index in range( 0, 2 ):
            name = 'library%s' % str( index + 1 )
            description = '%s description' % name
            synopsis = '%s synopsis' % name
            self.create_library( name=name, description=description, synopsis=synopsis )
        # Get the libraries for later use
        global library1
        library1 = get_library( 'library1', 'library1 description', 'library1 synopsis' )
        assert library1 is not None, 'Problem retrieving library (library1) from the database'
        global library2
        library2 = get_library( 'library2', 'library2 description', 'library2 synopsis' )
        assert library2 is not None, 'Problem retrieving library (library2) from the database'
        # setup add_library_item permission to regular_user1
        # Set permissions on the library, sort for later testing.
        permissions_in = [ 'LIBRARY_ACCESS' ]
        permissions_out = []
        # Role1 members are: admin_user, regular_user1, regular_user3.  
        # Each of these users will be permitted for LIBRARY_ACCESS, LIBRARY_ADD on 
        # library1 and library2.
        for library in [ library1, library2 ]:
            self.library_permissions( self.security.encode_id( library.id ),
                                      library.name,
                                      str( role1.id ),
                                      permissions_in,
                                      permissions_out )
        # adding a folder
        for library in [ library1, library2 ]:
            name = "%s_folder1" % library.name
            description = "%s description" % name
            self.add_folder( 'library_admin',
                             self.security.encode_id( library.id ),
                             self.security.encode_id( library.root_folder.id ),
                             name=name,
                             description=description )
        global library1_folder1
        library1_folder1 = get_folder( library1.root_folder.id, 'library1_folder1', 'library1_folder1 description' )
        assert library1_folder1 is not None, 'Problem retrieving library folder named "library1_folder1" from the database'
        global library2_folder1
        library2_folder1 = get_folder( library2.root_folder.id, 'library2_folder1', 'library2_folder1 description' )
        assert library2_folder1 is not None, 'Problem retrieving library folder named "library2_folder1" from the database'
    #
    # ====== Form definition test methods ================================================ 
    #
    def test_010_create_request_form_definition( self ):
        """Testing creating a sequencing request form definition, editing the name and description and adding fields"""
        # Logged in as admin_user
        # Create a form definition
        tmp_name = "Temp form"
        tmp_desc = "Temp form description"
        form_type = galaxy.model.FormDefinition.types.REQUEST
        self.create_form( name=tmp_name,
                          desc=tmp_desc,
                          form_type=form_type,
                          num_fields=0,
                          strings_displayed=[ 'Create a new form definition' ],
                          strings_displayed_after_submit=[ tmp_name, tmp_desc, form_type ] )
        tmp_form = get_form( tmp_name )
        # Edit the name and description of the form definition, and add 3 fields.
        new_name = "Request Form"
        new_desc = "Request Form description"
        global request_field_name1
        request_field_name1 = 'Request form field1'
        global request_field_name2
        request_field_name2 = 'Request form field2'
        global request_field_name3
        request_field_name3 = 'Request form field3'
        field_dicts = [ dict( name=request_field_name1,
                             desc='Description of '+request_field_name1,
                             type='SelectField',
                             required='optional',
                             selectlist=[ 'option1', 'option2' ] ),
                        dict( name=request_field_name2,
                              desc='Description of '+request_field_name2,
                              type='AddressField',
                              required='optional' ),
                        dict( name=request_field_name3,
                              desc='Description of '+request_field_name3,
                              type='TextField',
                              required='required' ) ]
        self.edit_form( id=self.security.encode_id( tmp_form.current.id ),
                        new_form_name=new_name,
                        new_form_desc=new_desc,
                        field_dicts=field_dicts,
                        field_index=len( tmp_form.fields ),
                        strings_displayed=[ 'Edit form definition "%s"' % tmp_name ],
                        strings_displayed_after_submit=[ "The form '%s' has been updated with the changes." % new_name ] )
        # Get the form_definition object for later tests
        global request_form_definition1
        request_form_definition1 = get_form( new_name )
        assert request_form_definition1 is not None, 'Problem retrieving form named "%s" from the database' % new_name
        assert len( request_form_definition1.fields ) == len( tmp_form.fields ) + len( field_dicts )
        # check form view
        self.view_form( id=self.security.encode_id( request_form_definition1.current.id ),
                        form_name=new_name,
                        form_desc=new_desc,
                        form_type=form_type,
                        field_dicts=field_dicts )
    def test_015_create_sample_form_definition( self ):
        """Testing creating sequencing sample form definition and adding fields"""
        name = "Sample Form"
        desc = "This is Sample Form's description"
        form_type = galaxy.model.FormDefinition.types.SAMPLE
        global sample_form_layout_grid_name
        sample_form_layout_grid_name = 'Layout Grid1'
        self.create_form( name=name,
                          desc=desc,
                          form_type=form_type,
                          form_layout_name=sample_form_layout_grid_name,
                          num_fields=0,
                          strings_displayed=[ 'Create a new form definition' ],
                          strings_displayed_after_submit=[ "The form '%s' has been updated with the changes." % name ] )
        tmp_form = get_form( name )
        # now add fields to the sample form definition
        global sample_field_name1
        sample_field_name1 = 'Sample form field1'
        global sample_field_name2
        sample_field_name2 = 'Sample form field2'
        global sample_field_name3
        sample_field_name3 = 'Sample form field3'
        field_dicts = [ dict( name=sample_field_name1,
                             desc='Description of '+sample_field_name1,
                             type='SelectField',
                             required='optional',
                             selectlist=[ 'option1', 'option2' ] ),
                        dict( name=sample_field_name2,
                              desc='Description of '+sample_field_name2,
                              type='TextField',
                              required='optional' ),
                        dict( name=sample_field_name3,
                              desc='Description of '+sample_field_name3,
                              type='TextField',
                              required='required' ) ]
        self.edit_form( id=self.security.encode_id( tmp_form.current.id ),
                        new_form_name=name,
                        new_form_desc=desc,
                        field_dicts=field_dicts,
                        field_index=len( tmp_form.fields ),
                        strings_displayed=[ 'Edit form definition "%s"' % name ],
                        strings_displayed_after_submit=[ "The form '%s' has been updated with the changes." % name ] )
        global sample_form_definition1
        sample_form_definition1 = get_form( name )
        assert sample_form_definition1 is not None, "Error retrieving form %s from db" % name
        print len( sample_form_definition1.fields ), len( field_dicts )
        print sample_form_definition1.fields
        print field_dicts
        assert len( sample_form_definition1.fields ) == len( field_dicts )
        # check form view
        self.view_form( id=self.security.encode_id( sample_form_definition1.current.id ),
                        form_name=name,
                        form_desc=desc,
                        form_type=form_type,
                        form_layout_name=sample_form_layout_grid_name,
                        field_dicts=field_dicts )
    def test_020_create_request_type( self ):
        """Testing creating a request_type"""
        name = 'Sequencer configuration1'
        self.create_request_type( name,
                                  "test sequencer configuration",
                                  self.security.encode_id( request_form_definition1.id ),
                                  self.security.encode_id( sample_form_definition1.id ),
                                  sample_states,
                                  strings_displayed=[ 'Create a new sequencer configuration' ],
                                  strings_displayed_after_submit=[ "Sequencer configuration (%s) has been created" % name ] )
        global request_type1
        request_type1 = get_request_type_by_name( name )
        assert request_type1 is not None, 'Problem retrieving sequencer configuration named "%s" from the database' % name
        # check view
        self.view_request_type( self.security.encode_id( request_type1.id ),
                                request_type1.name,
                                strings_displayed=[ request_form_definition1.name,
                                                    sample_form_definition1.name ],
                                sample_states=sample_states)
        # Set permissions
        permissions_in = [ k for k, v in galaxy.model.RequestType.permitted_actions.items() ]
        permissions_out = []
        # Role1 members are: admin_user, regular_user1, regular_user3.  Each of these users will be permitted for
        # REQUEST_TYPE_ACCESS on this request_type
        self.request_type_permissions( self.security.encode_id( request_type1.id ),
                                       request_type1.name,
                                       str( role1.id ),
                                       permissions_in,
                                       permissions_out )
        # Make sure the request_type1 is not accessible by regular_user2 since regular_user2 does not have Role1.
        self.logout()
        self.login( email=regular_user2.email )
        self.visit_url( '%s/requests_common/create_request?cntrller=requests&request_type=True' % self.url )
        try:
            self.check_page_for_string( 'There are no sequencer configurations created for a new request.' )
            raise AssertionError, 'The request_type %s is accessible by %s when it should be restricted' % ( request_type1.name, regular_user2.email )
        except:
            pass
        self.logout()
        self.login( email=admin_user.email )
    #
    # ====== Sequencing request test methods - User perspective ================ 
    #
    def test_025_create_request( self ):
        """Testing creating a sequencing request as a regular user"""
        # logged in as admin_user
        # Create a user_address
        self.logout()
        self.login( email=regular_user1.email )
        self.add_user_address( regular_user1.id, address_dict )
        global user_address1
        user_address1 = get_user_address( regular_user1, address_dict[ 'short_desc' ] )
        # Set field values - the tuples in the field_values list include the field_value, and True if refresh_on_change
        # is required for that field.
        field_value_tuples = [ ( 'option1', False ), ( str( user_address1.id ), True ), ( 'field3 value', False ) ] 
        # Create the request
        name = 'Request1'
        desc = 'Request1 Description'
        self.create_request( cntrller='requests',
                             request_type_id=self.security.encode_id( request_type1.id ),
                             name=name,
                             desc=desc,
                             field_value_tuples=field_value_tuples,
                             strings_displayed=[ 'Create a new sequencing request',
                                                 request_field_name1,
                                                 request_field_name2,
                                                 request_field_name3 ],
                             strings_displayed_after_submit=[ name, desc ] )
        global request1
        request1 = get_request_by_name( name )        
        # Make sure the request's state is now set to NEW
        assert request1.state is not request1.states.NEW, "The state of the request '%s' should be set to '%s'" \
            % ( request1.name, request1.states.NEW )
        # check request page
        self.view_request( cntrller='requests',
                           request_id=self.security.encode_id( request1.id ),
                           strings_displayed=[ 'Sequencing request "%s"' % request1.name,
                                               'There are no samples.' ],
                           strings_not_displayed=[ request1.states.SUBMITTED,
                                                   request1.states.COMPLETE,
                                                   request1.states.REJECTED,
                                                   'Submit request' ] ) # this button should NOT show up as there are no samples yet
        # check if the request is showing in the 'new' filter
        self.check_request_grid( cntrller='requests',
                                 state=request1.states.NEW,
                                 strings_displayed=[ request1.name ] )
        self.view_request_history( cntrller='requests',
                                   request_id=self.security.encode_id( request1.id ),
                                   strings_displayed=[ 'History of sequencing request "%s"' % request1.name,
                                                       request1.states.NEW,
                                                       'Request created' ],
                                   strings_not_displayed=[ request1.states.SUBMITTED,
                                                           request1.states.COMPLETE,
                                                           request1.states.REJECTED ] )
    def test_030_edit_basic_request_info( self ):
        """Testing editing the basic information and email settings of a sequencing request"""
        # logged in as regular_user1
        fields = [ 'option2', str( user_address1.id ), 'field3 value (edited)' ]
        new_name=request1.name + ' (Renamed)'
        new_desc=request1.desc + ' (Re-described)'
        self.edit_basic_request_info( request_id=self.security.encode_id( request1.id ),
                                      cntrller='requests',
                                      name=request1.name,
                                      new_name=new_name, 
                                      new_desc=new_desc,
                                      new_fields=fields,
                                      strings_displayed=[ 'Edit sequencing request "%s"' % request1.name ],
                                      strings_displayed_after_submit=[ new_name, new_desc ] )
        refresh( request1 )
        # now check email notification settings
        check_sample_states = [ ( request1.type.states[0].name, request1.type.states[0].id, True ),
                                ( request1.type.states[2].name, request1.type.states[2].id, True ),
                                ( request1.type.states[4].name, request1.type.states[4].id, True ) ]#[ ( state.id, True ) for state in request1.type.states ]
        strings_displayed = [ 'Edit sequencing request "%s"' % request1.name,
                              'Email notification settings' ]
        additional_emails = [ 'test@.bx.psu.edu', 'test2@.bx.psu.edu' ]
        strings_displayed_after_submit = [ "The changes made to the email notification settings have been saved",
                                           '\r\n'.join( additional_emails ) ]
        self.edit_request_email_settings( cntrller='requests', 
                                          request_id=self.security.encode_id( request1.id ), 
                                          check_request_owner=True, 
                                          additional_emails='\r\n'.join( additional_emails ), 
                                          check_sample_states=check_sample_states, 
                                          strings_displayed=strings_displayed, 
                                          strings_displayed_after_submit=strings_displayed_after_submit )
        # lastly check the details in the request page
        strings_displayed = [ 'Sequencing request "%s"' % new_name,
                              new_desc ]
        for field in fields:
            strings_displayed.append( field )        
        for state_name, id, is_checked in check_sample_states:
            strings_displayed.append( state_name )
        for email in additional_emails:
            strings_displayed.append( email )
        self.view_request( cntrller='requests',
                           request_id=self.security.encode_id( request1.id ),
                           strings_displayed=strings_displayed,
                           strings_not_displayed=[] )
    def test_035_add_samples_to_request( self ):
        """Testing adding samples to request"""
        # logged in as regular_user1
        # Sample fields - the tuple represents a sample name and a list of sample form field values
        target_library_info = dict(library=self.security.encode_id(library2.id), 
                                   folder=self.security.encode_id(library2_folder1.id) )
        sample_value_tuples = \
        [ ( 'Sample1', target_library_info, [ 'option1', 'sample1 field2 value', 'sample1 field3 value' ] ),
          ( 'Sample2', target_library_info, [ 'option2', 'sample2 field2 value', 'sample2 field3 value' ] ),
          ( 'Sample3', target_library_info, [ 'option1', 'sample3 field2 value', 'sample3 field3 value' ] ) ]
        strings_displayed_after_submit = [ 'Unsubmitted' ]
        for sample_name, lib_info, field_values in sample_value_tuples:
            strings_displayed_after_submit.append( sample_name )
            # add the sample values too
            for values in field_values:
                strings_displayed_after_submit.append( values )
        # Add samples to the request
        self.add_samples( cntrller='requests',
                          request_id=self.security.encode_id( request1.id ),
                          sample_value_tuples=sample_value_tuples,
                          strings_displayed=[ 'Add Samples to Request "%s"' % request1.name,
                                              '<input type="text" name="sample_0_name" value="Sample_1" size="10"/>' ], # sample name input field
                          strings_displayed_after_submit=strings_displayed_after_submit )
        # check the new sample field values on the request page
        strings_displayed = [ 'Sequencing request "%s"' % request1.name,
                              'Submit request' ] # this button should appear now
        strings_displayed.extend( strings_displayed_after_submit )
        strings_displayed_count = []
        strings_displayed_count.append( ( library2.name, len( sample_value_tuples ) ) )
        strings_displayed_count.append( ( library2_folder1.name, len( sample_value_tuples ) ) )
        self.view_request( cntrller='requests',
                           request_id=self.security.encode_id( request1.id ),
                           strings_displayed=strings_displayed,
                           strings_displayed_count=strings_displayed_count )
    def test_040_edit_samples_of_new_request( self ):
        """Testing editing the sample information of new request1"""
        # logged in as regular_user1
        # target data library - change it to library1
        target_library_info = dict(library=self.security.encode_id(library1.id), 
                                   folder=self.security.encode_id(library1_folder1.id) )
        new_sample_value_tuples = \
        [ ( 'Sample1_renamed', target_library_info, [ 'option2', 'sample1 field2 value edited', 'sample1 field3 value edited' ] ),
          ( 'Sample2_renamed', target_library_info, [ 'option1', 'sample2 field2 value edited', 'sample2 field3 value edited' ] ),
          ( 'Sample3_renamed', target_library_info, [ 'option2', 'sample3 field2 value edited', 'sample3 field3 value edited' ] ) ]
        strings_displayed_after_submit = [ 'Unsubmitted' ]
        for sample_name, lib_info, field_values in new_sample_value_tuples:
            strings_displayed_after_submit.append( sample_name )
            # add the sample values too
            for values in field_values:
                strings_displayed_after_submit.append( values )
        # Add samples to the request
        self.edit_samples( cntrller='requests',
                           request_id=self.security.encode_id( request1.id ),
                           sample_value_tuples=new_sample_value_tuples,
                           strings_displayed=[ 'Edit Current Samples of Request "%s"' % request1.name,
                                               '<input type="text" name="sample_0_name" value="Sample1" size="10"/>' ], # sample name input field
                           strings_displayed_after_submit=strings_displayed_after_submit )
        # check the changed sample field values on the request page
        strings_displayed = [ 'Sequencing request "%s"' % request1.name ]
        strings_displayed.extend( strings_displayed_after_submit )
        strings_displayed_count = []
        strings_displayed_count.append( ( library1.name, len( new_sample_value_tuples ) ) )
        strings_displayed_count.append( ( library1_folder1.name, len( new_sample_value_tuples ) ) )
        self.view_request( cntrller='requests',
                           request_id=self.security.encode_id( request1.id ),
                           strings_displayed=strings_displayed,
                           strings_displayed_count=strings_displayed_count )
    def test_045_submit_request( self ):
        """Testing submitting a sequencing request"""
        # logged in as regular_user1
        self.submit_request( cntrller='requests',
                             request_id=self.security.encode_id( request1.id ),
                             request_name=request1.name,
                             strings_displayed_after_submit=[ 'The request has been submitted.' ] )
        refresh( request1 )
        # Make sure the request is showing in the 'submitted' filter
        self.check_request_grid( cntrller='requests',
                                 state=request1.states.SUBMITTED,
                                 strings_displayed=[ request1.name ] )
        # Make sure the request's state is now set to 'submitted'
        assert request1.state is not request1.states.SUBMITTED, "The state of the request '%s' should be set to '%s'" \
            % ( request1.name, request1.states.SUBMITTED )
        # the sample state should appear once for each sample
        strings_displayed_count = [ ( request1.type.states[0].name, len( request1.samples ) ) ]
        # after submission, these buttons should not appear 
        strings_not_displayed = [ 'Add sample', 'Submit request' ]
        # check the request page
        self.view_request( cntrller='requests',
                           request_id=self.security.encode_id( request1.id ),
                           strings_displayed=[ request1.states.SUBMITTED ],
                           strings_displayed_count=strings_displayed_count,
                           strings_not_displayed=strings_not_displayed )
        strings_displayed=[ 'History of sequencing request "%s"' % request1.name,
                            'Request submitted by %s' % regular_user1.email,
                            'Request created' ]
        strings_displayed_count = [ ( request1.states.SUBMITTED, 1 ) ]
        self.view_request_history( cntrller='requests',
                                   request_id=self.security.encode_id( request1.id ),
                                   strings_displayed=strings_displayed,
                                   strings_displayed_count=strings_displayed_count,
                                   strings_not_displayed=[ request1.states.COMPLETE,
                                                           request1.states.REJECTED ] )
    #
    # ====== Sequencing request test methods - Admin perspective ================ 
    #
    def test_050_receive_request_as_admin( self ):
        """Testing receiving a sequencing request and assigning it barcodes"""
        self.logout()
        self.login( email=admin_user.email )
        self.check_request_grid( cntrller='requests_admin',
                                 state=request1.states.SUBMITTED,
                                 strings_displayed=[ request1.name ] )
        strings_displayed = [ request1.states.SUBMITTED,
                              'Reject this request' ]
        strings_not_displayed = [ 'Add sample' ]
        self.view_request( cntrller='requests_admin',
                           request_id=self.security.encode_id( request1.id ),
                           strings_not_displayed=strings_not_displayed )
        # Set bar codes for the samples
        bar_codes = [ '10001', '10002', '10003' ]
        strings_displayed_after_submit = [ 'Changes made to the samples have been saved.' ]
        strings_displayed_after_submit.extend( bar_codes )
        self.add_bar_codes( cntrller='requests_admin',
                            request_id=self.security.encode_id( request1.id ),
                            bar_codes=bar_codes,
                            strings_displayed=[ 'Edit Current Samples of Request "%s"' % request1.name ],
                            strings_displayed_after_submit=strings_displayed_after_submit )
        # the second sample state should appear once for each sample
        strings_displayed_count = [ ( request1.type.states[1].name, len( request1.samples ) ),
                                    ( request1.type.states[0].name, 0 ) ]        
        # check the request page
        self.view_request( cntrller='requests_admin',
                           request_id=self.security.encode_id( request1.id ),
                           strings_displayed=bar_codes,
                           strings_displayed_count=strings_displayed_count )
        # the sample state descriptions of the future states should not appear
        # here the state names are not checked as all of them appear at the top of
        # the page like: state1 > state2 > state3
        strings_not_displayed=[ request1.type.states[2].desc,
                                request1.type.states[3].desc,
                                request1.type.states[4].desc ]
        # check history of each sample
        for sample in request1.samples:
            strings_displayed = [ 'Events for Sample "%s"' % sample.name,
                                  'Request submitted and sample state set to %s' % request1.type.states[0].name,
                                   request1.type.states[0].name,
                                   request1.type.states[1].name ]
            self.view_sample_history( cntrller='requests_admin',
                                      sample_id=self.security.encode_id( sample.id ),
                                      strings_displayed=strings_displayed,
                                      strings_not_displayed=strings_not_displayed )
#    def test_040_request_lifecycle( self ):
#        """Testing request life-cycle as it goes through all the states"""
#        # logged in as regular_user1
#        self.logout()
#        self.login( email=admin_user.email )
#        self.check_request_grid( cntrller='requests_admin',
#                                 state=request1.states.SUBMITTED,
#                                 strings_displayed=[ request1.name ] )
#        self.visit_url( "%s/requests_common/view_request?cntrller=requests&id=%s" % ( self.url, self.security.encode_id( request1.id ) ) )
#        # TODO: add some string for checking on the page above...
#        # Set bar codes for the samples
#        bar_codes = [ '1234567890', '0987654321' ]
#        strings_displayed_after_submit=[ 'Changes made to the samples have been saved.' ]
#        for bar_code in bar_codes:
#            strings_displayed_after_submit.append( bar_code )
#        self.add_bar_codes( request_id=self.security.encode_id( request1.id ),
#                            request_name=request1.name,
#                            bar_codes=bar_codes,
#                            samples=request1.samples,
#                            strings_displayed_after_submit=strings_displayed_after_submit )
#        # Change the states of all the samples of this request to ultimately be COMPLETE
#        self.change_sample_state( request_id=self.security.encode_id( request1.id ),
#                                  request_name=request1.name,
#                                  sample_names=[ sample.name for sample in request1.samples ],
#                                  sample_ids=[ sample.id for sample in request1.samples ],
#                                  new_sample_state_id=request_type1.states[1].id,
#                                  new_state_name=request_type1.states[1].name )
#        self.change_sample_state( request_id=self.security.encode_id( request1.id ),
#                                  request_name=request1.name,
#                                  sample_names=[ sample.name for sample in request1.samples ],
#                                  sample_ids=[ sample.id for sample in request1.samples ],
#                                  new_sample_state_id=request_type1.states[2].id,
#                                  new_state_name=request_type1.states[2].name )
#        refresh( request1 )
#        self.logout()
#        self.login( email=regular_user1.email )
#        # check if the request's state is now set to 'complete'
#        self.check_request_grid( cntrller='requests',
#                                 state='Complete',
#                                 strings_displayed=[ request1.name ] )
#        assert request1.state is not request1.states.COMPLETE, "The state of the request '%s' should be set to '%s'" \
#            % ( request1.name, request1.states.COMPLETE )
#        
#    def test_045_admin_create_request_on_behalf_of_regular_user( self ):
#        """Testing creating and submitting a request as an admin on behalf of a regular user"""
#        # Logged in as regular_user1
#        self.logout()
#        self.login( email=admin_user.email )
#        # Create the request
#        name = "Request2"
#        desc = 'Request2 Description'
#        # Set field values - the tuples in the field_values list include the field_value, and True if refresh_on_change
#        # is required for that field.
#        field_value_tuples = [ ( 'option2', False ), ( str( user_address1.id ), True ), ( 'field_2_value', False ) ] 
#        self.create_request( cntrller='requests_admin',
#                             request_type_id=self.security.encode_id( request_type1.id ),
#                             other_users_id=self.security.encode_id( regular_user1.id ),
#                             name=name,
#                             desc=desc,
#                             field_value_tuples=field_value_tuples,
#                             strings_displayed=[ 'Create a new sequencing request',
#                                                 request_field_name1,
#                                                 request_field_name2,
#                                                 request_field_name3 ],
#                             strings_displayed_after_submit=[ "The request has been created." ] )
#        global request2
#        request2 = get_request_by_name( name )      
#        # Make sure the request is showing in the 'new' filter
#        self.check_request_grid( cntrller='requests_admin',
#                                 state=request2.states.NEW,
#                                 strings_displayed=[ request2.name ] )
#        # Make sure the request's state is now set to 'new'
#        assert request2.state is not request2.states.NEW, "The state of the request '%s' should be set to '%s'" \
#            % ( request2.name, request2.states.NEW )
#        # Sample fields - the tuple represents a sample name and a list of sample form field values
#        sample_value_tuples = [ ( 'Sample1', [ 'S1 Field 0 Value' ] ),
#                                ( 'Sample2', [ 'S2 Field 0 Value' ] ) ]
#        strings_displayed_after_submit = [ 'Unsubmitted' ]
#        for sample_name, field_values in sample_value_tuples:
#            strings_displayed_after_submit.append( sample_name )
#        # Add samples to the request
#        self.add_samples( cntrller='requests_admin',
#                          request_id=self.security.encode_id( request2.id ),
#                          request_name=request2.name,
#                          sample_value_tuples=sample_value_tuples,
#                          strings_displayed=[ 'There are no samples.' ],
#                          strings_displayed_after_submit=strings_displayed_after_submit )
#        # Submit the request
#        self.submit_request( cntrller='requests_admin',
#                             request_id=self.security.encode_id( request2.id ),
#                             request_name=request2.name,
#                             strings_displayed_after_submit=[ 'The request has been submitted.' ] )
#        refresh( request2 )
#        # Make sure the request is showing in the 'submitted' filter
#        self.check_request_grid( cntrller='requests_admin',
#                                 state=request2.states.SUBMITTED,
#                                 strings_displayed=[ request2.name ] )
#        # Make sure the request's state is now set to 'submitted'
#        assert request2.state is not request2.states.SUBMITTED, "The state of the request '%s' should be set to '%s'" \
#            % ( request2.name, request2.states.SUBMITTED )
#        # Make sure both requests are showing in the 'All' filter
#        self.check_request_grid( cntrller='requests_admin',
#                                 state='All',
#                                 strings_displayed=[ request1.name, request2.name ] )
#    def test_050_reject_request( self ):
#        """Testing rejecting a request"""
#        # Logged in as admin_user
#        self.reject_request( request_id=self.security.encode_id( request2.id ),
#                             request_name=request2.name,
#                             comment="Rejection test comment",
#                             strings_displayed=[ 'Reject Sequencing Request "%s"' % request2.name ],
#                             strings_displayed_after_submit=[ 'Request (%s) has been rejected.' % request2.name ] )
#        refresh( request2 )
#        # Make sure the request is showing in the 'rejected' filter
#        self.check_request_grid( cntrller='requests_admin',
#                                 state=request2.states.REJECTED,
#                                 strings_displayed=[ request2.name ] )
#        # Make sure the request's state is now set to REJECTED
#        assert request2.state is not request2.states.REJECTED, "The state of the request '%s' should be set to '%s'" \
#            % ( request2.name, request2.states.REJECTED )
    def test_055_reset_data_for_later_test_runs( self ):
        """Reseting data to enable later test runs to pass"""
        # Logged in as admin_user
        self.logout()
        self.login( email=admin_user.email )
        ##################
        # Purge all libraries
        ##################
        for library in [ library1, library2 ]:
            self.delete_library_item( 'library_admin',
                                      self.security.encode_id( library.id ),
                                      self.security.encode_id( library.id ),
                                      library.name,
                                      item_type='library' )
            self.purge_library( self.security.encode_id( library.id ), library.name )

        ##################
        # Delete request_type permissions
        ##################
        for request_type in [ request_type1 ]:
            delete_request_type_permissions( request_type.id )
        ##################
        # Mark all request_types deleted
        ##################
        for request_type in [ request_type1 ]:
            mark_obj_deleted( request_type )
        ##################
        # Mark all requests deleted
        ##################
        for request in [ request1 ]:
            mark_obj_deleted( request )
        ##################
        # Mark all forms deleted
        ##################
        for form in [ request_form_definition1, sample_form_definition1 ]:
            self.mark_form_deleted( self.security.encode_id( form.current.id ) )
        ##################
        # Mark all user_addresses deleted
        ##################
        for user_address in [ user_address1 ]:
            mark_obj_deleted( user_address )
        ##################
        # Delete all non-private roles
        ##################
        for role in [ role1, role2 ]:
            self.mark_role_deleted( self.security.encode_id( role.id ), role.name )
            self.purge_role( self.security.encode_id( role.id ), role.name )
            # Manually delete the role from the database
            refresh( role )
            delete_obj( role )
        ##################
        # Delete all groups
        ##################
        for group in [ group1 ]:
            self.mark_group_deleted( self.security.encode_id( group.id ), group.name )
            self.purge_group( self.security.encode_id( group.id ), group.name )
            # Manually delete the group from the database
            refresh( group )
            delete_obj( group )
