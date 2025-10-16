"""Update models for ANT compliance

Revision ID: 001
Revises: 
Create Date: 2024-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ENUM types will be created automatically by the column definitions
    # (using postgresql.ENUM in the table DDL). Avoid creating them twice.
    
    # Crear tabla usuarios
    op.create_table('usuarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('correo', sa.String(length=255), nullable=False),
        sa.Column('telefono', sa.String(length=32), nullable=True),
        sa.Column('contrasena_hash', sa.String(length=255), nullable=False),
        sa.Column('rol', postgresql.ENUM('cliente', 'conductor', 'admin', name='user_role'), nullable=False),
        sa.Column('nombre_completo', sa.String(length=255), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('creado_en', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_usuarios_correo', 'usuarios', ['correo'], unique=True)
    
    # Crear tabla perfil_conductor
    op.create_table('perfil_conductor',
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('licencia_numero', sa.String(), nullable=False),
        sa.Column('licencia_categoria', sa.String(), nullable=False),
        sa.Column('licencia_vigente', sa.Boolean(), nullable=False),
        sa.Column('licencia_documento', sa.String(), nullable=True),
        sa.Column('documento_respaldo', sa.String(), nullable=True),
        sa.Column('verificado', sa.Boolean(), nullable=False),
        sa.Column('verificado_por', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fecha_verificacion', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('promedio_calificacion', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('total_calificaciones', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['verificado_por'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('usuario_id')
    )
    
    # Crear tabla vehiculos
    op.create_table('vehiculos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conductor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('placa', sa.String(), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('capacidad_kg', sa.Integer(), nullable=False),
        sa.Column('documento_respaldo', sa.String(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('creado_en', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conductor_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('placa')
    )
    op.create_index('ix_vehiculos_conductor', 'vehiculos', ['conductor_id'])
    
    # Crear tabla ordenes
    op.create_table('ordenes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cliente_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conductor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('estado', postgresql.ENUM('pendiente', 'aceptada', 'en_curso', 'completada', 'cancelada', name='order_status'), nullable=False),
        sa.Column('direccion_origen', sa.String(), nullable=False),
        sa.Column('lat_origen', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('lng_origen', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('direccion_destino', sa.String(), nullable=False),
        sa.Column('lat_destino', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('lng_destino', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('distancia_km', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('tiempo_estimado_min', sa.Integer(), nullable=True),
        sa.Column('precio_estimado', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('creado_en', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('actualizado_en', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['conductor_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ordenes_estado', 'ordenes', ['estado'])
    op.create_index('ix_ordenes_cliente', 'ordenes', ['cliente_id'])
    op.create_index('ix_ordenes_conductor', 'ordenes', ['conductor_id'])
    
    # Crear tabla eventos_orden
    op.create_table('eventos_orden',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('orden_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_evento', sa.String(), nullable=False),
        sa.Column('usuario_actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('origen', postgresql.ENUM('cliente', 'conductor', 'admin', 'sistema', name='evento_origen'), nullable=False),
        sa.Column('detalles', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('creado_en', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['orden_id'], ['ordenes.id'], ),
        sa.ForeignKeyConstraint(['usuario_actor_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eventos_orden_id', 'eventos_orden', ['orden_id'])
    op.create_index('ix_eventos_usuario_actor', 'eventos_orden', ['usuario_actor_id'])
    
    # Crear tabla mensajes_chat
    op.create_table('mensajes_chat',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('orden_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('remitente_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mensaje', sa.String(), nullable=False),
        sa.Column('enviado_en', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['orden_id'], ['ordenes.id'], ),
        sa.ForeignKeyConstraint(['remitente_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chat_orden', 'mensajes_chat', ['orden_id'])
    
    # Crear tabla disponibilidad_conductor
    op.create_table('disponibilidad_conductor',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('conductor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('disponible', sa.Boolean(), nullable=False),
        sa.Column('zona', sa.String(), nullable=True),
        sa.Column('latitud', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('longitud', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('actualizado_en', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conductor_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_disp_conductor', 'disponibilidad_conductor', ['conductor_id'])
    op.create_index('ix_disp_zona', 'disponibilidad_conductor', ['zona'])
    
    # Crear tabla calificaciones
    op.create_table('calificaciones',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('orden_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_califica_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_calificado_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('puntaje', sa.SmallInteger(), nullable=False),
        sa.Column('comentario', sa.String(), nullable=True),
        sa.Column('creado_en', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['orden_id'], ['ordenes.id'], ),
        sa.ForeignKeyConstraint(['usuario_califica_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['usuario_calificado_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rating_usuario_calificado', 'calificaciones', ['usuario_calificado_id'])
    op.create_index('ix_rating_orden_usuario', 'calificaciones', ['orden_id', 'usuario_califica_id'], unique=True)


def downgrade() -> None:
    # Eliminar tablas en orden inverso
    op.drop_index('ix_rating_orden_usuario', table_name='calificaciones')
    op.drop_index('ix_rating_usuario_calificado', table_name='calificaciones')
    op.drop_table('calificaciones')
    
    op.drop_index('ix_disp_zona', table_name='disponibilidad_conductor')
    op.drop_index('ix_disp_conductor', table_name='disponibilidad_conductor')
    op.drop_table('disponibilidad_conductor')
    
    op.drop_index('ix_chat_orden', table_name='mensajes_chat')
    op.drop_table('mensajes_chat')
    
    op.drop_index('ix_eventos_usuario_actor', table_name='eventos_orden')
    op.drop_index('ix_eventos_orden_id', table_name='eventos_orden')
    op.drop_table('eventos_orden')
    
    op.drop_index('ix_ordenes_conductor', table_name='ordenes')
    op.drop_index('ix_ordenes_cliente', table_name='ordenes')
    op.drop_index('ix_ordenes_estado', table_name='ordenes')
    op.drop_table('ordenes')
    
    op.drop_index('ix_vehiculos_conductor', table_name='vehiculos')
    op.drop_table('vehiculos')
    
    op.drop_table('perfil_conductor')
    
    op.drop_index('ix_usuarios_correo', table_name='usuarios')
    op.drop_table('usuarios')
    
    # Eliminar tipos ENUM
    op.execute("DROP TYPE evento_origen")
    op.execute("DROP TYPE order_status")
    op.execute("DROP TYPE user_role")
