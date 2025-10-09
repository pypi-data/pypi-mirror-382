# encoding: utf-8

from south.db import db
from south.v2 import SchemaMigration

from m3_django_compatibility import AUTH_USER_MODEL


class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UserRole'
        db.create_table('m3_users_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('metarole', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('m3_users', ['UserRole'])

        # Adding model 'RolePermission'
        db.create_table('m3_users_rolepermissions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['m3_users.UserRole'])),
            ('permission_code', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('verbose_permission_name', self.gf('django.db.models.fields.TextField')()),
            ('disabled', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('m3_users', ['RolePermission'])

        # Adding model 'AssignedRole'
        db.create_table('m3_users_assignedrole', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[AUTH_USER_MODEL])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['m3_users.UserRole'])),
        ))
        db.send_create_signal('m3_users', ['AssignedRole'])


    def backwards(self, orm):
        
        # Deleting model 'UserRole'
        db.delete_table('m3_users_role')

        # Deleting model 'RolePermission'
        db.delete_table('m3_users_rolepermissions')

        # Deleting model 'AssignedRole'
        db.delete_table('m3_users_assignedrole')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'm3_users.assignedrole': {
            'Meta': {'object_name': 'AssignedRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['m3_users.UserRole']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{}']".format(AUTH_USER_MODEL)})
        },
        'm3_users.rolepermission': {
            'Meta': {'object_name': 'RolePermission', 'db_table': "'m3_users_rolepermissions'"},
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission_code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['m3_users.UserRole']"}),
            'verbose_permission_name': ('django.db.models.fields.TextField', [], {})
        },
        'm3_users.userrole': {
            'Meta': {'object_name': 'UserRole', 'db_table': "'m3_users_role'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metarole': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        }
    }

    complete_apps = ['m3_users']
