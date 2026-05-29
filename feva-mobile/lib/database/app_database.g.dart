// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_database.dart';

// ignore_for_file: type=lint
class $SessionsTable extends Sessions with TableInfo<$SessionsTable, Session> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SessionsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _userIdMeta = const VerificationMeta('userId');
  @override
  late final GeneratedColumn<String> userId = GeneratedColumn<String>(
      'user_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _usernameMeta =
      const VerificationMeta('username');
  @override
  late final GeneratedColumn<String> username = GeneratedColumn<String>(
      'username', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _roleMeta = const VerificationMeta('role');
  @override
  late final GeneratedColumn<String> role = GeneratedColumn<String>(
      'role', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _lgaCodeMeta =
      const VerificationMeta('lgaCode');
  @override
  late final GeneratedColumn<String> lgaCode = GeneratedColumn<String>(
      'lga_code', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _wardMeta = const VerificationMeta('ward');
  @override
  late final GeneratedColumn<String> ward = GeneratedColumn<String>(
      'ward', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _accessTokenMeta =
      const VerificationMeta('accessToken');
  @override
  late final GeneratedColumn<String> accessToken = GeneratedColumn<String>(
      'access_token', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _refreshTokenMeta =
      const VerificationMeta('refreshToken');
  @override
  late final GeneratedColumn<String> refreshToken = GeneratedColumn<String>(
      'refresh_token', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _tokenExpiresAtMeta =
      const VerificationMeta('tokenExpiresAt');
  @override
  late final GeneratedColumn<int> tokenExpiresAt = GeneratedColumn<int>(
      'token_expires_at', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<int> createdAt = GeneratedColumn<int>(
      'created_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _passwordHashMeta =
      const VerificationMeta('passwordHash');
  @override
  late final GeneratedColumn<String> passwordHash = GeneratedColumn<String>(
      'password_hash', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        userId,
        username,
        role,
        lgaCode,
        ward,
        accessToken,
        refreshToken,
        tokenExpiresAt,
        createdAt,
        passwordHash
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sessions';
  @override
  VerificationContext validateIntegrity(Insertable<Session> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('user_id')) {
      context.handle(_userIdMeta,
          userId.isAcceptableOrUnknown(data['user_id']!, _userIdMeta));
    } else if (isInserting) {
      context.missing(_userIdMeta);
    }
    if (data.containsKey('username')) {
      context.handle(_usernameMeta,
          username.isAcceptableOrUnknown(data['username']!, _usernameMeta));
    } else if (isInserting) {
      context.missing(_usernameMeta);
    }
    if (data.containsKey('role')) {
      context.handle(
          _roleMeta, role.isAcceptableOrUnknown(data['role']!, _roleMeta));
    } else if (isInserting) {
      context.missing(_roleMeta);
    }
    if (data.containsKey('lga_code')) {
      context.handle(_lgaCodeMeta,
          lgaCode.isAcceptableOrUnknown(data['lga_code']!, _lgaCodeMeta));
    }
    if (data.containsKey('ward')) {
      context.handle(
          _wardMeta, ward.isAcceptableOrUnknown(data['ward']!, _wardMeta));
    }
    if (data.containsKey('access_token')) {
      context.handle(
          _accessTokenMeta,
          accessToken.isAcceptableOrUnknown(
              data['access_token']!, _accessTokenMeta));
    } else if (isInserting) {
      context.missing(_accessTokenMeta);
    }
    if (data.containsKey('refresh_token')) {
      context.handle(
          _refreshTokenMeta,
          refreshToken.isAcceptableOrUnknown(
              data['refresh_token']!, _refreshTokenMeta));
    } else if (isInserting) {
      context.missing(_refreshTokenMeta);
    }
    if (data.containsKey('token_expires_at')) {
      context.handle(
          _tokenExpiresAtMeta,
          tokenExpiresAt.isAcceptableOrUnknown(
              data['token_expires_at']!, _tokenExpiresAtMeta));
    } else if (isInserting) {
      context.missing(_tokenExpiresAtMeta);
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    if (data.containsKey('password_hash')) {
      context.handle(
          _passwordHashMeta,
          passwordHash.isAcceptableOrUnknown(
              data['password_hash']!, _passwordHashMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Session map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Session(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      userId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}user_id'])!,
      username: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}username'])!,
      role: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}role'])!,
      lgaCode: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}lga_code']),
      ward: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}ward']),
      accessToken: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}access_token'])!,
      refreshToken: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}refresh_token'])!,
      tokenExpiresAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}token_expires_at'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}created_at'])!,
      passwordHash: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}password_hash']),
    );
  }

  @override
  $SessionsTable createAlias(String alias) {
    return $SessionsTable(attachedDatabase, alias);
  }
}

class Session extends DataClass implements Insertable<Session> {
  final int id;
  final String userId;
  final String username;
  final String role;
  final String? lgaCode;
  final String? ward;
  final String accessToken;
  final String refreshToken;
  final int tokenExpiresAt;
  final int createdAt;
  final String? passwordHash;
  const Session(
      {required this.id,
      required this.userId,
      required this.username,
      required this.role,
      this.lgaCode,
      this.ward,
      required this.accessToken,
      required this.refreshToken,
      required this.tokenExpiresAt,
      required this.createdAt,
      this.passwordHash});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['user_id'] = Variable<String>(userId);
    map['username'] = Variable<String>(username);
    map['role'] = Variable<String>(role);
    if (!nullToAbsent || lgaCode != null) {
      map['lga_code'] = Variable<String>(lgaCode);
    }
    if (!nullToAbsent || ward != null) {
      map['ward'] = Variable<String>(ward);
    }
    map['access_token'] = Variable<String>(accessToken);
    map['refresh_token'] = Variable<String>(refreshToken);
    map['token_expires_at'] = Variable<int>(tokenExpiresAt);
    map['created_at'] = Variable<int>(createdAt);
    if (!nullToAbsent || passwordHash != null) {
      map['password_hash'] = Variable<String>(passwordHash);
    }
    return map;
  }

  SessionsCompanion toCompanion(bool nullToAbsent) {
    return SessionsCompanion(
      id: Value(id),
      userId: Value(userId),
      username: Value(username),
      role: Value(role),
      lgaCode: lgaCode == null && nullToAbsent
          ? const Value.absent()
          : Value(lgaCode),
      ward: ward == null && nullToAbsent ? const Value.absent() : Value(ward),
      accessToken: Value(accessToken),
      refreshToken: Value(refreshToken),
      tokenExpiresAt: Value(tokenExpiresAt),
      createdAt: Value(createdAt),
      passwordHash: passwordHash == null && nullToAbsent
          ? const Value.absent()
          : Value(passwordHash),
    );
  }

  factory Session.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Session(
      id: serializer.fromJson<int>(json['id']),
      userId: serializer.fromJson<String>(json['userId']),
      username: serializer.fromJson<String>(json['username']),
      role: serializer.fromJson<String>(json['role']),
      lgaCode: serializer.fromJson<String?>(json['lgaCode']),
      ward: serializer.fromJson<String?>(json['ward']),
      accessToken: serializer.fromJson<String>(json['accessToken']),
      refreshToken: serializer.fromJson<String>(json['refreshToken']),
      tokenExpiresAt: serializer.fromJson<int>(json['tokenExpiresAt']),
      createdAt: serializer.fromJson<int>(json['createdAt']),
      passwordHash: serializer.fromJson<String?>(json['passwordHash']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'userId': serializer.toJson<String>(userId),
      'username': serializer.toJson<String>(username),
      'role': serializer.toJson<String>(role),
      'lgaCode': serializer.toJson<String?>(lgaCode),
      'ward': serializer.toJson<String?>(ward),
      'accessToken': serializer.toJson<String>(accessToken),
      'refreshToken': serializer.toJson<String>(refreshToken),
      'tokenExpiresAt': serializer.toJson<int>(tokenExpiresAt),
      'createdAt': serializer.toJson<int>(createdAt),
      'passwordHash': serializer.toJson<String?>(passwordHash),
    };
  }

  Session copyWith(
          {int? id,
          String? userId,
          String? username,
          String? role,
          Value<String?> lgaCode = const Value.absent(),
          Value<String?> ward = const Value.absent(),
          String? accessToken,
          String? refreshToken,
          int? tokenExpiresAt,
          int? createdAt,
          Value<String?> passwordHash = const Value.absent()}) =>
      Session(
        id: id ?? this.id,
        userId: userId ?? this.userId,
        username: username ?? this.username,
        role: role ?? this.role,
        lgaCode: lgaCode.present ? lgaCode.value : this.lgaCode,
        ward: ward.present ? ward.value : this.ward,
        accessToken: accessToken ?? this.accessToken,
        refreshToken: refreshToken ?? this.refreshToken,
        tokenExpiresAt: tokenExpiresAt ?? this.tokenExpiresAt,
        createdAt: createdAt ?? this.createdAt,
        passwordHash:
            passwordHash.present ? passwordHash.value : this.passwordHash,
      );
  Session copyWithCompanion(SessionsCompanion data) {
    return Session(
      id: data.id.present ? data.id.value : this.id,
      userId: data.userId.present ? data.userId.value : this.userId,
      username: data.username.present ? data.username.value : this.username,
      role: data.role.present ? data.role.value : this.role,
      lgaCode: data.lgaCode.present ? data.lgaCode.value : this.lgaCode,
      ward: data.ward.present ? data.ward.value : this.ward,
      accessToken:
          data.accessToken.present ? data.accessToken.value : this.accessToken,
      refreshToken: data.refreshToken.present
          ? data.refreshToken.value
          : this.refreshToken,
      tokenExpiresAt: data.tokenExpiresAt.present
          ? data.tokenExpiresAt.value
          : this.tokenExpiresAt,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      passwordHash: data.passwordHash.present
          ? data.passwordHash.value
          : this.passwordHash,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Session(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('username: $username, ')
          ..write('role: $role, ')
          ..write('lgaCode: $lgaCode, ')
          ..write('ward: $ward, ')
          ..write('accessToken: $accessToken, ')
          ..write('refreshToken: $refreshToken, ')
          ..write('tokenExpiresAt: $tokenExpiresAt, ')
          ..write('createdAt: $createdAt, ')
          ..write('passwordHash: $passwordHash')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, userId, username, role, lgaCode, ward,
      accessToken, refreshToken, tokenExpiresAt, createdAt, passwordHash);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Session &&
          other.id == this.id &&
          other.userId == this.userId &&
          other.username == this.username &&
          other.role == this.role &&
          other.lgaCode == this.lgaCode &&
          other.ward == this.ward &&
          other.accessToken == this.accessToken &&
          other.refreshToken == this.refreshToken &&
          other.tokenExpiresAt == this.tokenExpiresAt &&
          other.createdAt == this.createdAt &&
          other.passwordHash == this.passwordHash);
}

class SessionsCompanion extends UpdateCompanion<Session> {
  final Value<int> id;
  final Value<String> userId;
  final Value<String> username;
  final Value<String> role;
  final Value<String?> lgaCode;
  final Value<String?> ward;
  final Value<String> accessToken;
  final Value<String> refreshToken;
  final Value<int> tokenExpiresAt;
  final Value<int> createdAt;
  final Value<String?> passwordHash;
  const SessionsCompanion({
    this.id = const Value.absent(),
    this.userId = const Value.absent(),
    this.username = const Value.absent(),
    this.role = const Value.absent(),
    this.lgaCode = const Value.absent(),
    this.ward = const Value.absent(),
    this.accessToken = const Value.absent(),
    this.refreshToken = const Value.absent(),
    this.tokenExpiresAt = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.passwordHash = const Value.absent(),
  });
  SessionsCompanion.insert({
    this.id = const Value.absent(),
    required String userId,
    required String username,
    required String role,
    this.lgaCode = const Value.absent(),
    this.ward = const Value.absent(),
    required String accessToken,
    required String refreshToken,
    required int tokenExpiresAt,
    this.createdAt = const Value.absent(),
    this.passwordHash = const Value.absent(),
  })  : userId = Value(userId),
        username = Value(username),
        role = Value(role),
        accessToken = Value(accessToken),
        refreshToken = Value(refreshToken),
        tokenExpiresAt = Value(tokenExpiresAt);
  static Insertable<Session> custom({
    Expression<int>? id,
    Expression<String>? userId,
    Expression<String>? username,
    Expression<String>? role,
    Expression<String>? lgaCode,
    Expression<String>? ward,
    Expression<String>? accessToken,
    Expression<String>? refreshToken,
    Expression<int>? tokenExpiresAt,
    Expression<int>? createdAt,
    Expression<String>? passwordHash,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (userId != null) 'user_id': userId,
      if (username != null) 'username': username,
      if (role != null) 'role': role,
      if (lgaCode != null) 'lga_code': lgaCode,
      if (ward != null) 'ward': ward,
      if (accessToken != null) 'access_token': accessToken,
      if (refreshToken != null) 'refresh_token': refreshToken,
      if (tokenExpiresAt != null) 'token_expires_at': tokenExpiresAt,
      if (createdAt != null) 'created_at': createdAt,
      if (passwordHash != null) 'password_hash': passwordHash,
    });
  }

  SessionsCompanion copyWith(
      {Value<int>? id,
      Value<String>? userId,
      Value<String>? username,
      Value<String>? role,
      Value<String?>? lgaCode,
      Value<String?>? ward,
      Value<String>? accessToken,
      Value<String>? refreshToken,
      Value<int>? tokenExpiresAt,
      Value<int>? createdAt,
      Value<String?>? passwordHash}) {
    return SessionsCompanion(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      username: username ?? this.username,
      role: role ?? this.role,
      lgaCode: lgaCode ?? this.lgaCode,
      ward: ward ?? this.ward,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      tokenExpiresAt: tokenExpiresAt ?? this.tokenExpiresAt,
      createdAt: createdAt ?? this.createdAt,
      passwordHash: passwordHash ?? this.passwordHash,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (userId.present) {
      map['user_id'] = Variable<String>(userId.value);
    }
    if (username.present) {
      map['username'] = Variable<String>(username.value);
    }
    if (role.present) {
      map['role'] = Variable<String>(role.value);
    }
    if (lgaCode.present) {
      map['lga_code'] = Variable<String>(lgaCode.value);
    }
    if (ward.present) {
      map['ward'] = Variable<String>(ward.value);
    }
    if (accessToken.present) {
      map['access_token'] = Variable<String>(accessToken.value);
    }
    if (refreshToken.present) {
      map['refresh_token'] = Variable<String>(refreshToken.value);
    }
    if (tokenExpiresAt.present) {
      map['token_expires_at'] = Variable<int>(tokenExpiresAt.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<int>(createdAt.value);
    }
    if (passwordHash.present) {
      map['password_hash'] = Variable<String>(passwordHash.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SessionsCompanion(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('username: $username, ')
          ..write('role: $role, ')
          ..write('lgaCode: $lgaCode, ')
          ..write('ward: $ward, ')
          ..write('accessToken: $accessToken, ')
          ..write('refreshToken: $refreshToken, ')
          ..write('tokenExpiresAt: $tokenExpiresAt, ')
          ..write('createdAt: $createdAt, ')
          ..write('passwordHash: $passwordHash')
          ..write(')'))
        .toString();
  }
}

class $DropdownConfigTable extends DropdownConfig
    with TableInfo<$DropdownConfigTable, DropdownConfigData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $DropdownConfigTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _categoryMeta =
      const VerificationMeta('category');
  @override
  late final GeneratedColumn<String> category = GeneratedColumn<String>(
      'category', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _valueMeta = const VerificationMeta('value');
  @override
  late final GeneratedColumn<String> value = GeneratedColumn<String>(
      'value', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _labelMeta = const VerificationMeta('label');
  @override
  late final GeneratedColumn<String> label = GeneratedColumn<String>(
      'label', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _sortOrderMeta =
      const VerificationMeta('sortOrder');
  @override
  late final GeneratedColumn<int> sortOrder = GeneratedColumn<int>(
      'sort_order', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _versionMeta =
      const VerificationMeta('version');
  @override
  late final GeneratedColumn<int> version = GeneratedColumn<int>(
      'version', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(1));
  static const VerificationMeta _syncedAtMeta =
      const VerificationMeta('syncedAt');
  @override
  late final GeneratedColumn<int> syncedAt = GeneratedColumn<int>(
      'synced_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  @override
  List<GeneratedColumn> get $columns =>
      [id, category, value, label, sortOrder, version, syncedAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'dropdown_config';
  @override
  VerificationContext validateIntegrity(Insertable<DropdownConfigData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('category')) {
      context.handle(_categoryMeta,
          category.isAcceptableOrUnknown(data['category']!, _categoryMeta));
    } else if (isInserting) {
      context.missing(_categoryMeta);
    }
    if (data.containsKey('value')) {
      context.handle(
          _valueMeta, value.isAcceptableOrUnknown(data['value']!, _valueMeta));
    } else if (isInserting) {
      context.missing(_valueMeta);
    }
    if (data.containsKey('label')) {
      context.handle(
          _labelMeta, label.isAcceptableOrUnknown(data['label']!, _labelMeta));
    } else if (isInserting) {
      context.missing(_labelMeta);
    }
    if (data.containsKey('sort_order')) {
      context.handle(_sortOrderMeta,
          sortOrder.isAcceptableOrUnknown(data['sort_order']!, _sortOrderMeta));
    }
    if (data.containsKey('version')) {
      context.handle(_versionMeta,
          version.isAcceptableOrUnknown(data['version']!, _versionMeta));
    }
    if (data.containsKey('synced_at')) {
      context.handle(_syncedAtMeta,
          syncedAt.isAcceptableOrUnknown(data['synced_at']!, _syncedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  List<Set<GeneratedColumn>> get uniqueKeys => [
        {category, value},
      ];
  @override
  DropdownConfigData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return DropdownConfigData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      category: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}category'])!,
      value: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}value'])!,
      label: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}label'])!,
      sortOrder: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}sort_order'])!,
      version: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}version'])!,
      syncedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}synced_at'])!,
    );
  }

  @override
  $DropdownConfigTable createAlias(String alias) {
    return $DropdownConfigTable(attachedDatabase, alias);
  }
}

class DropdownConfigData extends DataClass
    implements Insertable<DropdownConfigData> {
  final int id;
  final String category;
  final String value;
  final String label;
  final int sortOrder;
  final int version;
  final int syncedAt;
  const DropdownConfigData(
      {required this.id,
      required this.category,
      required this.value,
      required this.label,
      required this.sortOrder,
      required this.version,
      required this.syncedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['category'] = Variable<String>(category);
    map['value'] = Variable<String>(value);
    map['label'] = Variable<String>(label);
    map['sort_order'] = Variable<int>(sortOrder);
    map['version'] = Variable<int>(version);
    map['synced_at'] = Variable<int>(syncedAt);
    return map;
  }

  DropdownConfigCompanion toCompanion(bool nullToAbsent) {
    return DropdownConfigCompanion(
      id: Value(id),
      category: Value(category),
      value: Value(value),
      label: Value(label),
      sortOrder: Value(sortOrder),
      version: Value(version),
      syncedAt: Value(syncedAt),
    );
  }

  factory DropdownConfigData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return DropdownConfigData(
      id: serializer.fromJson<int>(json['id']),
      category: serializer.fromJson<String>(json['category']),
      value: serializer.fromJson<String>(json['value']),
      label: serializer.fromJson<String>(json['label']),
      sortOrder: serializer.fromJson<int>(json['sortOrder']),
      version: serializer.fromJson<int>(json['version']),
      syncedAt: serializer.fromJson<int>(json['syncedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'category': serializer.toJson<String>(category),
      'value': serializer.toJson<String>(value),
      'label': serializer.toJson<String>(label),
      'sortOrder': serializer.toJson<int>(sortOrder),
      'version': serializer.toJson<int>(version),
      'syncedAt': serializer.toJson<int>(syncedAt),
    };
  }

  DropdownConfigData copyWith(
          {int? id,
          String? category,
          String? value,
          String? label,
          int? sortOrder,
          int? version,
          int? syncedAt}) =>
      DropdownConfigData(
        id: id ?? this.id,
        category: category ?? this.category,
        value: value ?? this.value,
        label: label ?? this.label,
        sortOrder: sortOrder ?? this.sortOrder,
        version: version ?? this.version,
        syncedAt: syncedAt ?? this.syncedAt,
      );
  DropdownConfigData copyWithCompanion(DropdownConfigCompanion data) {
    return DropdownConfigData(
      id: data.id.present ? data.id.value : this.id,
      category: data.category.present ? data.category.value : this.category,
      value: data.value.present ? data.value.value : this.value,
      label: data.label.present ? data.label.value : this.label,
      sortOrder: data.sortOrder.present ? data.sortOrder.value : this.sortOrder,
      version: data.version.present ? data.version.value : this.version,
      syncedAt: data.syncedAt.present ? data.syncedAt.value : this.syncedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('DropdownConfigData(')
          ..write('id: $id, ')
          ..write('category: $category, ')
          ..write('value: $value, ')
          ..write('label: $label, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('version: $version, ')
          ..write('syncedAt: $syncedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(id, category, value, label, sortOrder, version, syncedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is DropdownConfigData &&
          other.id == this.id &&
          other.category == this.category &&
          other.value == this.value &&
          other.label == this.label &&
          other.sortOrder == this.sortOrder &&
          other.version == this.version &&
          other.syncedAt == this.syncedAt);
}

class DropdownConfigCompanion extends UpdateCompanion<DropdownConfigData> {
  final Value<int> id;
  final Value<String> category;
  final Value<String> value;
  final Value<String> label;
  final Value<int> sortOrder;
  final Value<int> version;
  final Value<int> syncedAt;
  const DropdownConfigCompanion({
    this.id = const Value.absent(),
    this.category = const Value.absent(),
    this.value = const Value.absent(),
    this.label = const Value.absent(),
    this.sortOrder = const Value.absent(),
    this.version = const Value.absent(),
    this.syncedAt = const Value.absent(),
  });
  DropdownConfigCompanion.insert({
    this.id = const Value.absent(),
    required String category,
    required String value,
    required String label,
    this.sortOrder = const Value.absent(),
    this.version = const Value.absent(),
    this.syncedAt = const Value.absent(),
  })  : category = Value(category),
        value = Value(value),
        label = Value(label);
  static Insertable<DropdownConfigData> custom({
    Expression<int>? id,
    Expression<String>? category,
    Expression<String>? value,
    Expression<String>? label,
    Expression<int>? sortOrder,
    Expression<int>? version,
    Expression<int>? syncedAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (category != null) 'category': category,
      if (value != null) 'value': value,
      if (label != null) 'label': label,
      if (sortOrder != null) 'sort_order': sortOrder,
      if (version != null) 'version': version,
      if (syncedAt != null) 'synced_at': syncedAt,
    });
  }

  DropdownConfigCompanion copyWith(
      {Value<int>? id,
      Value<String>? category,
      Value<String>? value,
      Value<String>? label,
      Value<int>? sortOrder,
      Value<int>? version,
      Value<int>? syncedAt}) {
    return DropdownConfigCompanion(
      id: id ?? this.id,
      category: category ?? this.category,
      value: value ?? this.value,
      label: label ?? this.label,
      sortOrder: sortOrder ?? this.sortOrder,
      version: version ?? this.version,
      syncedAt: syncedAt ?? this.syncedAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (category.present) {
      map['category'] = Variable<String>(category.value);
    }
    if (value.present) {
      map['value'] = Variable<String>(value.value);
    }
    if (label.present) {
      map['label'] = Variable<String>(label.value);
    }
    if (sortOrder.present) {
      map['sort_order'] = Variable<int>(sortOrder.value);
    }
    if (version.present) {
      map['version'] = Variable<int>(version.value);
    }
    if (syncedAt.present) {
      map['synced_at'] = Variable<int>(syncedAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('DropdownConfigCompanion(')
          ..write('id: $id, ')
          ..write('category: $category, ')
          ..write('value: $value, ')
          ..write('label: $label, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('version: $version, ')
          ..write('syncedAt: $syncedAt')
          ..write(')'))
        .toString();
  }
}

class $BoundaryZonesTable extends BoundaryZones
    with TableInfo<$BoundaryZonesTable, BoundaryZone> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $BoundaryZonesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _zoneIdMeta = const VerificationMeta('zoneId');
  @override
  late final GeneratedColumn<String> zoneId = GeneratedColumn<String>(
      'zone_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways('UNIQUE'));
  static const VerificationMeta _zoneNameMeta =
      const VerificationMeta('zoneName');
  @override
  late final GeneratedColumn<String> zoneName = GeneratedColumn<String>(
      'zone_name', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _zoneTypeMeta =
      const VerificationMeta('zoneType');
  @override
  late final GeneratedColumn<String> zoneType = GeneratedColumn<String>(
      'zone_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _lgaCodeMeta =
      const VerificationMeta('lgaCode');
  @override
  late final GeneratedColumn<String> lgaCode = GeneratedColumn<String>(
      'lga_code', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _wardCodeMeta =
      const VerificationMeta('wardCode');
  @override
  late final GeneratedColumn<String> wardCode = GeneratedColumn<String>(
      'ward_code', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _postcodeMeta =
      const VerificationMeta('postcode');
  @override
  late final GeneratedColumn<String> postcode = GeneratedColumn<String>(
      'postcode', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _geometryWkbMeta =
      const VerificationMeta('geometryWkb');
  @override
  late final GeneratedColumn<Uint8List> geometryWkb =
      GeneratedColumn<Uint8List>('geometry_wkb', aliasedName, false,
          type: DriftSqlType.blob, requiredDuringInsert: true);
  static const VerificationMeta _shapefileVersionMeta =
      const VerificationMeta('shapefileVersion');
  @override
  late final GeneratedColumn<String> shapefileVersion = GeneratedColumn<String>(
      'shapefile_version', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<int> createdAt = GeneratedColumn<int>(
      'created_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  @override
  List<GeneratedColumn> get $columns => [
        id,
        zoneId,
        zoneName,
        zoneType,
        lgaCode,
        wardCode,
        postcode,
        geometryWkb,
        shapefileVersion,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'boundary_zones';
  @override
  VerificationContext validateIntegrity(Insertable<BoundaryZone> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('zone_id')) {
      context.handle(_zoneIdMeta,
          zoneId.isAcceptableOrUnknown(data['zone_id']!, _zoneIdMeta));
    } else if (isInserting) {
      context.missing(_zoneIdMeta);
    }
    if (data.containsKey('zone_name')) {
      context.handle(_zoneNameMeta,
          zoneName.isAcceptableOrUnknown(data['zone_name']!, _zoneNameMeta));
    } else if (isInserting) {
      context.missing(_zoneNameMeta);
    }
    if (data.containsKey('zone_type')) {
      context.handle(_zoneTypeMeta,
          zoneType.isAcceptableOrUnknown(data['zone_type']!, _zoneTypeMeta));
    } else if (isInserting) {
      context.missing(_zoneTypeMeta);
    }
    if (data.containsKey('lga_code')) {
      context.handle(_lgaCodeMeta,
          lgaCode.isAcceptableOrUnknown(data['lga_code']!, _lgaCodeMeta));
    }
    if (data.containsKey('ward_code')) {
      context.handle(_wardCodeMeta,
          wardCode.isAcceptableOrUnknown(data['ward_code']!, _wardCodeMeta));
    }
    if (data.containsKey('postcode')) {
      context.handle(_postcodeMeta,
          postcode.isAcceptableOrUnknown(data['postcode']!, _postcodeMeta));
    }
    if (data.containsKey('geometry_wkb')) {
      context.handle(
          _geometryWkbMeta,
          geometryWkb.isAcceptableOrUnknown(
              data['geometry_wkb']!, _geometryWkbMeta));
    } else if (isInserting) {
      context.missing(_geometryWkbMeta);
    }
    if (data.containsKey('shapefile_version')) {
      context.handle(
          _shapefileVersionMeta,
          shapefileVersion.isAcceptableOrUnknown(
              data['shapefile_version']!, _shapefileVersionMeta));
    } else if (isInserting) {
      context.missing(_shapefileVersionMeta);
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  BoundaryZone map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return BoundaryZone(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      zoneId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}zone_id'])!,
      zoneName: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}zone_name'])!,
      zoneType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}zone_type'])!,
      lgaCode: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}lga_code']),
      wardCode: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}ward_code']),
      postcode: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}postcode']),
      geometryWkb: attachedDatabase.typeMapping
          .read(DriftSqlType.blob, data['${effectivePrefix}geometry_wkb'])!,
      shapefileVersion: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}shapefile_version'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $BoundaryZonesTable createAlias(String alias) {
    return $BoundaryZonesTable(attachedDatabase, alias);
  }
}

class BoundaryZone extends DataClass implements Insertable<BoundaryZone> {
  final int id;
  final String zoneId;
  final String zoneName;
  final String zoneType;
  final String? lgaCode;
  final String? wardCode;
  final String? postcode;
  final Uint8List geometryWkb;
  final String shapefileVersion;
  final int createdAt;
  const BoundaryZone(
      {required this.id,
      required this.zoneId,
      required this.zoneName,
      required this.zoneType,
      this.lgaCode,
      this.wardCode,
      this.postcode,
      required this.geometryWkb,
      required this.shapefileVersion,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['zone_id'] = Variable<String>(zoneId);
    map['zone_name'] = Variable<String>(zoneName);
    map['zone_type'] = Variable<String>(zoneType);
    if (!nullToAbsent || lgaCode != null) {
      map['lga_code'] = Variable<String>(lgaCode);
    }
    if (!nullToAbsent || wardCode != null) {
      map['ward_code'] = Variable<String>(wardCode);
    }
    if (!nullToAbsent || postcode != null) {
      map['postcode'] = Variable<String>(postcode);
    }
    map['geometry_wkb'] = Variable<Uint8List>(geometryWkb);
    map['shapefile_version'] = Variable<String>(shapefileVersion);
    map['created_at'] = Variable<int>(createdAt);
    return map;
  }

  BoundaryZonesCompanion toCompanion(bool nullToAbsent) {
    return BoundaryZonesCompanion(
      id: Value(id),
      zoneId: Value(zoneId),
      zoneName: Value(zoneName),
      zoneType: Value(zoneType),
      lgaCode: lgaCode == null && nullToAbsent
          ? const Value.absent()
          : Value(lgaCode),
      wardCode: wardCode == null && nullToAbsent
          ? const Value.absent()
          : Value(wardCode),
      postcode: postcode == null && nullToAbsent
          ? const Value.absent()
          : Value(postcode),
      geometryWkb: Value(geometryWkb),
      shapefileVersion: Value(shapefileVersion),
      createdAt: Value(createdAt),
    );
  }

  factory BoundaryZone.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return BoundaryZone(
      id: serializer.fromJson<int>(json['id']),
      zoneId: serializer.fromJson<String>(json['zoneId']),
      zoneName: serializer.fromJson<String>(json['zoneName']),
      zoneType: serializer.fromJson<String>(json['zoneType']),
      lgaCode: serializer.fromJson<String?>(json['lgaCode']),
      wardCode: serializer.fromJson<String?>(json['wardCode']),
      postcode: serializer.fromJson<String?>(json['postcode']),
      geometryWkb: serializer.fromJson<Uint8List>(json['geometryWkb']),
      shapefileVersion: serializer.fromJson<String>(json['shapefileVersion']),
      createdAt: serializer.fromJson<int>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'zoneId': serializer.toJson<String>(zoneId),
      'zoneName': serializer.toJson<String>(zoneName),
      'zoneType': serializer.toJson<String>(zoneType),
      'lgaCode': serializer.toJson<String?>(lgaCode),
      'wardCode': serializer.toJson<String?>(wardCode),
      'postcode': serializer.toJson<String?>(postcode),
      'geometryWkb': serializer.toJson<Uint8List>(geometryWkb),
      'shapefileVersion': serializer.toJson<String>(shapefileVersion),
      'createdAt': serializer.toJson<int>(createdAt),
    };
  }

  BoundaryZone copyWith(
          {int? id,
          String? zoneId,
          String? zoneName,
          String? zoneType,
          Value<String?> lgaCode = const Value.absent(),
          Value<String?> wardCode = const Value.absent(),
          Value<String?> postcode = const Value.absent(),
          Uint8List? geometryWkb,
          String? shapefileVersion,
          int? createdAt}) =>
      BoundaryZone(
        id: id ?? this.id,
        zoneId: zoneId ?? this.zoneId,
        zoneName: zoneName ?? this.zoneName,
        zoneType: zoneType ?? this.zoneType,
        lgaCode: lgaCode.present ? lgaCode.value : this.lgaCode,
        wardCode: wardCode.present ? wardCode.value : this.wardCode,
        postcode: postcode.present ? postcode.value : this.postcode,
        geometryWkb: geometryWkb ?? this.geometryWkb,
        shapefileVersion: shapefileVersion ?? this.shapefileVersion,
        createdAt: createdAt ?? this.createdAt,
      );
  BoundaryZone copyWithCompanion(BoundaryZonesCompanion data) {
    return BoundaryZone(
      id: data.id.present ? data.id.value : this.id,
      zoneId: data.zoneId.present ? data.zoneId.value : this.zoneId,
      zoneName: data.zoneName.present ? data.zoneName.value : this.zoneName,
      zoneType: data.zoneType.present ? data.zoneType.value : this.zoneType,
      lgaCode: data.lgaCode.present ? data.lgaCode.value : this.lgaCode,
      wardCode: data.wardCode.present ? data.wardCode.value : this.wardCode,
      postcode: data.postcode.present ? data.postcode.value : this.postcode,
      geometryWkb:
          data.geometryWkb.present ? data.geometryWkb.value : this.geometryWkb,
      shapefileVersion: data.shapefileVersion.present
          ? data.shapefileVersion.value
          : this.shapefileVersion,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('BoundaryZone(')
          ..write('id: $id, ')
          ..write('zoneId: $zoneId, ')
          ..write('zoneName: $zoneName, ')
          ..write('zoneType: $zoneType, ')
          ..write('lgaCode: $lgaCode, ')
          ..write('wardCode: $wardCode, ')
          ..write('postcode: $postcode, ')
          ..write('geometryWkb: $geometryWkb, ')
          ..write('shapefileVersion: $shapefileVersion, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      zoneId,
      zoneName,
      zoneType,
      lgaCode,
      wardCode,
      postcode,
      $driftBlobEquality.hash(geometryWkb),
      shapefileVersion,
      createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is BoundaryZone &&
          other.id == this.id &&
          other.zoneId == this.zoneId &&
          other.zoneName == this.zoneName &&
          other.zoneType == this.zoneType &&
          other.lgaCode == this.lgaCode &&
          other.wardCode == this.wardCode &&
          other.postcode == this.postcode &&
          $driftBlobEquality.equals(other.geometryWkb, this.geometryWkb) &&
          other.shapefileVersion == this.shapefileVersion &&
          other.createdAt == this.createdAt);
}

class BoundaryZonesCompanion extends UpdateCompanion<BoundaryZone> {
  final Value<int> id;
  final Value<String> zoneId;
  final Value<String> zoneName;
  final Value<String> zoneType;
  final Value<String?> lgaCode;
  final Value<String?> wardCode;
  final Value<String?> postcode;
  final Value<Uint8List> geometryWkb;
  final Value<String> shapefileVersion;
  final Value<int> createdAt;
  const BoundaryZonesCompanion({
    this.id = const Value.absent(),
    this.zoneId = const Value.absent(),
    this.zoneName = const Value.absent(),
    this.zoneType = const Value.absent(),
    this.lgaCode = const Value.absent(),
    this.wardCode = const Value.absent(),
    this.postcode = const Value.absent(),
    this.geometryWkb = const Value.absent(),
    this.shapefileVersion = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  BoundaryZonesCompanion.insert({
    this.id = const Value.absent(),
    required String zoneId,
    required String zoneName,
    required String zoneType,
    this.lgaCode = const Value.absent(),
    this.wardCode = const Value.absent(),
    this.postcode = const Value.absent(),
    required Uint8List geometryWkb,
    required String shapefileVersion,
    this.createdAt = const Value.absent(),
  })  : zoneId = Value(zoneId),
        zoneName = Value(zoneName),
        zoneType = Value(zoneType),
        geometryWkb = Value(geometryWkb),
        shapefileVersion = Value(shapefileVersion);
  static Insertable<BoundaryZone> custom({
    Expression<int>? id,
    Expression<String>? zoneId,
    Expression<String>? zoneName,
    Expression<String>? zoneType,
    Expression<String>? lgaCode,
    Expression<String>? wardCode,
    Expression<String>? postcode,
    Expression<Uint8List>? geometryWkb,
    Expression<String>? shapefileVersion,
    Expression<int>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (zoneId != null) 'zone_id': zoneId,
      if (zoneName != null) 'zone_name': zoneName,
      if (zoneType != null) 'zone_type': zoneType,
      if (lgaCode != null) 'lga_code': lgaCode,
      if (wardCode != null) 'ward_code': wardCode,
      if (postcode != null) 'postcode': postcode,
      if (geometryWkb != null) 'geometry_wkb': geometryWkb,
      if (shapefileVersion != null) 'shapefile_version': shapefileVersion,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  BoundaryZonesCompanion copyWith(
      {Value<int>? id,
      Value<String>? zoneId,
      Value<String>? zoneName,
      Value<String>? zoneType,
      Value<String?>? lgaCode,
      Value<String?>? wardCode,
      Value<String?>? postcode,
      Value<Uint8List>? geometryWkb,
      Value<String>? shapefileVersion,
      Value<int>? createdAt}) {
    return BoundaryZonesCompanion(
      id: id ?? this.id,
      zoneId: zoneId ?? this.zoneId,
      zoneName: zoneName ?? this.zoneName,
      zoneType: zoneType ?? this.zoneType,
      lgaCode: lgaCode ?? this.lgaCode,
      wardCode: wardCode ?? this.wardCode,
      postcode: postcode ?? this.postcode,
      geometryWkb: geometryWkb ?? this.geometryWkb,
      shapefileVersion: shapefileVersion ?? this.shapefileVersion,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (zoneId.present) {
      map['zone_id'] = Variable<String>(zoneId.value);
    }
    if (zoneName.present) {
      map['zone_name'] = Variable<String>(zoneName.value);
    }
    if (zoneType.present) {
      map['zone_type'] = Variable<String>(zoneType.value);
    }
    if (lgaCode.present) {
      map['lga_code'] = Variable<String>(lgaCode.value);
    }
    if (wardCode.present) {
      map['ward_code'] = Variable<String>(wardCode.value);
    }
    if (postcode.present) {
      map['postcode'] = Variable<String>(postcode.value);
    }
    if (geometryWkb.present) {
      map['geometry_wkb'] = Variable<Uint8List>(geometryWkb.value);
    }
    if (shapefileVersion.present) {
      map['shapefile_version'] = Variable<String>(shapefileVersion.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<int>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('BoundaryZonesCompanion(')
          ..write('id: $id, ')
          ..write('zoneId: $zoneId, ')
          ..write('zoneName: $zoneName, ')
          ..write('zoneType: $zoneType, ')
          ..write('lgaCode: $lgaCode, ')
          ..write('wardCode: $wardCode, ')
          ..write('postcode: $postcode, ')
          ..write('geometryWkb: $geometryWkb, ')
          ..write('shapefileVersion: $shapefileVersion, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

class $StreetsTable extends Streets with TableInfo<$StreetsTable, Street> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $StreetsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _streetIdMeta =
      const VerificationMeta('streetId');
  @override
  late final GeneratedColumn<String> streetId = GeneratedColumn<String>(
      'street_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways('UNIQUE'));
  static const VerificationMeta _streetNameMeta =
      const VerificationMeta('streetName');
  @override
  late final GeneratedColumn<String> streetName = GeneratedColumn<String>(
      'street_name', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _streetAddressMeta =
      const VerificationMeta('streetAddress');
  @override
  late final GeneratedColumn<String> streetAddress = GeneratedColumn<String>(
      'street_address', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant(''));
  static const VerificationMeta _streetTypeMeta =
      const VerificationMeta('streetType');
  @override
  late final GeneratedColumn<String> streetType = GeneratedColumn<String>(
      'street_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _surfaceTypeMeta =
      const VerificationMeta('surfaceType');
  @override
  late final GeneratedColumn<String> surfaceType = GeneratedColumn<String>(
      'surface_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _streetConditionMeta =
      const VerificationMeta('streetCondition');
  @override
  late final GeneratedColumn<String> streetCondition = GeneratedColumn<String>(
      'street_condition', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _notesMeta = const VerificationMeta('notes');
  @override
  late final GeneratedColumn<String> notes = GeneratedColumn<String>(
      'notes', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _geometryWkbMeta =
      const VerificationMeta('geometryWkb');
  @override
  late final GeneratedColumn<Uint8List> geometryWkb =
      GeneratedColumn<Uint8List>('geometry_wkb', aliasedName, false,
          type: DriftSqlType.blob, requiredDuringInsert: true);
  static const VerificationMeta _zoneMeta = const VerificationMeta('zone');
  @override
  late final GeneratedColumn<String> zone = GeneratedColumn<String>(
      'zone', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _lgaMeta = const VerificationMeta('lga');
  @override
  late final GeneratedColumn<String> lga = GeneratedColumn<String>(
      'lga', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _wardMeta = const VerificationMeta('ward');
  @override
  late final GeneratedColumn<String> ward = GeneratedColumn<String>(
      'ward', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _enumeratorIdMeta =
      const VerificationMeta('enumeratorId');
  @override
  late final GeneratedColumn<String> enumeratorId = GeneratedColumn<String>(
      'enumerator_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _enumerationDateMeta =
      const VerificationMeta('enumerationDate');
  @override
  late final GeneratedColumn<int> enumerationDate = GeneratedColumn<int>(
      'enumeration_date', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _verificationStatusMeta =
      const VerificationMeta('verificationStatus');
  @override
  late final GeneratedColumn<String> verificationStatus =
      GeneratedColumn<String>('verification_status', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: false,
          defaultValue: const Constant('pending'));
  static const VerificationMeta _boundaryFlagMeta =
      const VerificationMeta('boundaryFlag');
  @override
  late final GeneratedColumn<int> boundaryFlag = GeneratedColumn<int>(
      'boundary_flag', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _gpsAccuracyFlagMeta =
      const VerificationMeta('gpsAccuracyFlag');
  @override
  late final GeneratedColumn<int> gpsAccuracyFlag = GeneratedColumn<int>(
      'gps_accuracy_flag', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _qaFlagsMeta =
      const VerificationMeta('qaFlags');
  @override
  late final GeneratedColumn<String> qaFlags = GeneratedColumn<String>(
      'qa_flags', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _serverIdMeta =
      const VerificationMeta('serverId');
  @override
  late final GeneratedColumn<String> serverId = GeneratedColumn<String>(
      'server_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _syncStatusMeta =
      const VerificationMeta('syncStatus');
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
      'sync_status', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('queued'));
  static const VerificationMeta _lastModifiedAtMeta =
      const VerificationMeta('lastModifiedAt');
  @override
  late final GeneratedColumn<int> lastModifiedAt = GeneratedColumn<int>(
      'last_modified_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<int> createdAt = GeneratedColumn<int>(
      'created_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  @override
  List<GeneratedColumn> get $columns => [
        id,
        streetId,
        streetName,
        streetAddress,
        streetType,
        surfaceType,
        streetCondition,
        notes,
        geometryWkb,
        zone,
        lga,
        ward,
        enumeratorId,
        enumerationDate,
        verificationStatus,
        boundaryFlag,
        gpsAccuracyFlag,
        qaFlags,
        serverId,
        syncStatus,
        lastModifiedAt,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'streets';
  @override
  VerificationContext validateIntegrity(Insertable<Street> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('street_id')) {
      context.handle(_streetIdMeta,
          streetId.isAcceptableOrUnknown(data['street_id']!, _streetIdMeta));
    } else if (isInserting) {
      context.missing(_streetIdMeta);
    }
    if (data.containsKey('street_name')) {
      context.handle(
          _streetNameMeta,
          streetName.isAcceptableOrUnknown(
              data['street_name']!, _streetNameMeta));
    } else if (isInserting) {
      context.missing(_streetNameMeta);
    }
    if (data.containsKey('street_address')) {
      context.handle(
          _streetAddressMeta,
          streetAddress.isAcceptableOrUnknown(
              data['street_address']!, _streetAddressMeta));
    }
    if (data.containsKey('street_type')) {
      context.handle(
          _streetTypeMeta,
          streetType.isAcceptableOrUnknown(
              data['street_type']!, _streetTypeMeta));
    } else if (isInserting) {
      context.missing(_streetTypeMeta);
    }
    if (data.containsKey('surface_type')) {
      context.handle(
          _surfaceTypeMeta,
          surfaceType.isAcceptableOrUnknown(
              data['surface_type']!, _surfaceTypeMeta));
    } else if (isInserting) {
      context.missing(_surfaceTypeMeta);
    }
    if (data.containsKey('street_condition')) {
      context.handle(
          _streetConditionMeta,
          streetCondition.isAcceptableOrUnknown(
              data['street_condition']!, _streetConditionMeta));
    } else if (isInserting) {
      context.missing(_streetConditionMeta);
    }
    if (data.containsKey('notes')) {
      context.handle(
          _notesMeta, notes.isAcceptableOrUnknown(data['notes']!, _notesMeta));
    }
    if (data.containsKey('geometry_wkb')) {
      context.handle(
          _geometryWkbMeta,
          geometryWkb.isAcceptableOrUnknown(
              data['geometry_wkb']!, _geometryWkbMeta));
    } else if (isInserting) {
      context.missing(_geometryWkbMeta);
    }
    if (data.containsKey('zone')) {
      context.handle(
          _zoneMeta, zone.isAcceptableOrUnknown(data['zone']!, _zoneMeta));
    }
    if (data.containsKey('lga')) {
      context.handle(
          _lgaMeta, lga.isAcceptableOrUnknown(data['lga']!, _lgaMeta));
    } else if (isInserting) {
      context.missing(_lgaMeta);
    }
    if (data.containsKey('ward')) {
      context.handle(
          _wardMeta, ward.isAcceptableOrUnknown(data['ward']!, _wardMeta));
    }
    if (data.containsKey('enumerator_id')) {
      context.handle(
          _enumeratorIdMeta,
          enumeratorId.isAcceptableOrUnknown(
              data['enumerator_id']!, _enumeratorIdMeta));
    } else if (isInserting) {
      context.missing(_enumeratorIdMeta);
    }
    if (data.containsKey('enumeration_date')) {
      context.handle(
          _enumerationDateMeta,
          enumerationDate.isAcceptableOrUnknown(
              data['enumeration_date']!, _enumerationDateMeta));
    } else if (isInserting) {
      context.missing(_enumerationDateMeta);
    }
    if (data.containsKey('verification_status')) {
      context.handle(
          _verificationStatusMeta,
          verificationStatus.isAcceptableOrUnknown(
              data['verification_status']!, _verificationStatusMeta));
    }
    if (data.containsKey('boundary_flag')) {
      context.handle(
          _boundaryFlagMeta,
          boundaryFlag.isAcceptableOrUnknown(
              data['boundary_flag']!, _boundaryFlagMeta));
    }
    if (data.containsKey('gps_accuracy_flag')) {
      context.handle(
          _gpsAccuracyFlagMeta,
          gpsAccuracyFlag.isAcceptableOrUnknown(
              data['gps_accuracy_flag']!, _gpsAccuracyFlagMeta));
    }
    if (data.containsKey('qa_flags')) {
      context.handle(_qaFlagsMeta,
          qaFlags.isAcceptableOrUnknown(data['qa_flags']!, _qaFlagsMeta));
    }
    if (data.containsKey('server_id')) {
      context.handle(_serverIdMeta,
          serverId.isAcceptableOrUnknown(data['server_id']!, _serverIdMeta));
    }
    if (data.containsKey('sync_status')) {
      context.handle(
          _syncStatusMeta,
          syncStatus.isAcceptableOrUnknown(
              data['sync_status']!, _syncStatusMeta));
    }
    if (data.containsKey('last_modified_at')) {
      context.handle(
          _lastModifiedAtMeta,
          lastModifiedAt.isAcceptableOrUnknown(
              data['last_modified_at']!, _lastModifiedAtMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Street map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Street(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      streetId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}street_id'])!,
      streetName: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}street_name'])!,
      streetAddress: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}street_address'])!,
      streetType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}street_type'])!,
      surfaceType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}surface_type'])!,
      streetCondition: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}street_condition'])!,
      notes: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}notes']),
      geometryWkb: attachedDatabase.typeMapping
          .read(DriftSqlType.blob, data['${effectivePrefix}geometry_wkb'])!,
      zone: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}zone']),
      lga: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}lga'])!,
      ward: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}ward']),
      enumeratorId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}enumerator_id'])!,
      enumerationDate: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}enumeration_date'])!,
      verificationStatus: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}verification_status'])!,
      boundaryFlag: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}boundary_flag'])!,
      gpsAccuracyFlag: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}gps_accuracy_flag'])!,
      qaFlags: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}qa_flags']),
      serverId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}server_id']),
      syncStatus: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}sync_status'])!,
      lastModifiedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}last_modified_at'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $StreetsTable createAlias(String alias) {
    return $StreetsTable(attachedDatabase, alias);
  }
}

class Street extends DataClass implements Insertable<Street> {
  final int id;
  final String streetId;
  final String streetName;
  final String streetAddress;
  final String streetType;
  final String surfaceType;
  final String streetCondition;
  final String? notes;
  final Uint8List geometryWkb;
  final String? zone;
  final String lga;
  final String? ward;
  final String enumeratorId;
  final int enumerationDate;
  final String verificationStatus;
  final int boundaryFlag;
  final int gpsAccuracyFlag;
  final String? qaFlags;
  final String? serverId;
  final String syncStatus;
  final int lastModifiedAt;
  final int createdAt;
  const Street(
      {required this.id,
      required this.streetId,
      required this.streetName,
      required this.streetAddress,
      required this.streetType,
      required this.surfaceType,
      required this.streetCondition,
      this.notes,
      required this.geometryWkb,
      this.zone,
      required this.lga,
      this.ward,
      required this.enumeratorId,
      required this.enumerationDate,
      required this.verificationStatus,
      required this.boundaryFlag,
      required this.gpsAccuracyFlag,
      this.qaFlags,
      this.serverId,
      required this.syncStatus,
      required this.lastModifiedAt,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['street_id'] = Variable<String>(streetId);
    map['street_name'] = Variable<String>(streetName);
    map['street_address'] = Variable<String>(streetAddress);
    map['street_type'] = Variable<String>(streetType);
    map['surface_type'] = Variable<String>(surfaceType);
    map['street_condition'] = Variable<String>(streetCondition);
    if (!nullToAbsent || notes != null) {
      map['notes'] = Variable<String>(notes);
    }
    map['geometry_wkb'] = Variable<Uint8List>(geometryWkb);
    if (!nullToAbsent || zone != null) {
      map['zone'] = Variable<String>(zone);
    }
    map['lga'] = Variable<String>(lga);
    if (!nullToAbsent || ward != null) {
      map['ward'] = Variable<String>(ward);
    }
    map['enumerator_id'] = Variable<String>(enumeratorId);
    map['enumeration_date'] = Variable<int>(enumerationDate);
    map['verification_status'] = Variable<String>(verificationStatus);
    map['boundary_flag'] = Variable<int>(boundaryFlag);
    map['gps_accuracy_flag'] = Variable<int>(gpsAccuracyFlag);
    if (!nullToAbsent || qaFlags != null) {
      map['qa_flags'] = Variable<String>(qaFlags);
    }
    if (!nullToAbsent || serverId != null) {
      map['server_id'] = Variable<String>(serverId);
    }
    map['sync_status'] = Variable<String>(syncStatus);
    map['last_modified_at'] = Variable<int>(lastModifiedAt);
    map['created_at'] = Variable<int>(createdAt);
    return map;
  }

  StreetsCompanion toCompanion(bool nullToAbsent) {
    return StreetsCompanion(
      id: Value(id),
      streetId: Value(streetId),
      streetName: Value(streetName),
      streetAddress: Value(streetAddress),
      streetType: Value(streetType),
      surfaceType: Value(surfaceType),
      streetCondition: Value(streetCondition),
      notes:
          notes == null && nullToAbsent ? const Value.absent() : Value(notes),
      geometryWkb: Value(geometryWkb),
      zone: zone == null && nullToAbsent ? const Value.absent() : Value(zone),
      lga: Value(lga),
      ward: ward == null && nullToAbsent ? const Value.absent() : Value(ward),
      enumeratorId: Value(enumeratorId),
      enumerationDate: Value(enumerationDate),
      verificationStatus: Value(verificationStatus),
      boundaryFlag: Value(boundaryFlag),
      gpsAccuracyFlag: Value(gpsAccuracyFlag),
      qaFlags: qaFlags == null && nullToAbsent
          ? const Value.absent()
          : Value(qaFlags),
      serverId: serverId == null && nullToAbsent
          ? const Value.absent()
          : Value(serverId),
      syncStatus: Value(syncStatus),
      lastModifiedAt: Value(lastModifiedAt),
      createdAt: Value(createdAt),
    );
  }

  factory Street.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Street(
      id: serializer.fromJson<int>(json['id']),
      streetId: serializer.fromJson<String>(json['streetId']),
      streetName: serializer.fromJson<String>(json['streetName']),
      streetAddress: serializer.fromJson<String>(json['streetAddress']),
      streetType: serializer.fromJson<String>(json['streetType']),
      surfaceType: serializer.fromJson<String>(json['surfaceType']),
      streetCondition: serializer.fromJson<String>(json['streetCondition']),
      notes: serializer.fromJson<String?>(json['notes']),
      geometryWkb: serializer.fromJson<Uint8List>(json['geometryWkb']),
      zone: serializer.fromJson<String?>(json['zone']),
      lga: serializer.fromJson<String>(json['lga']),
      ward: serializer.fromJson<String?>(json['ward']),
      enumeratorId: serializer.fromJson<String>(json['enumeratorId']),
      enumerationDate: serializer.fromJson<int>(json['enumerationDate']),
      verificationStatus:
          serializer.fromJson<String>(json['verificationStatus']),
      boundaryFlag: serializer.fromJson<int>(json['boundaryFlag']),
      gpsAccuracyFlag: serializer.fromJson<int>(json['gpsAccuracyFlag']),
      qaFlags: serializer.fromJson<String?>(json['qaFlags']),
      serverId: serializer.fromJson<String?>(json['serverId']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      lastModifiedAt: serializer.fromJson<int>(json['lastModifiedAt']),
      createdAt: serializer.fromJson<int>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'streetId': serializer.toJson<String>(streetId),
      'streetName': serializer.toJson<String>(streetName),
      'streetAddress': serializer.toJson<String>(streetAddress),
      'streetType': serializer.toJson<String>(streetType),
      'surfaceType': serializer.toJson<String>(surfaceType),
      'streetCondition': serializer.toJson<String>(streetCondition),
      'notes': serializer.toJson<String?>(notes),
      'geometryWkb': serializer.toJson<Uint8List>(geometryWkb),
      'zone': serializer.toJson<String?>(zone),
      'lga': serializer.toJson<String>(lga),
      'ward': serializer.toJson<String?>(ward),
      'enumeratorId': serializer.toJson<String>(enumeratorId),
      'enumerationDate': serializer.toJson<int>(enumerationDate),
      'verificationStatus': serializer.toJson<String>(verificationStatus),
      'boundaryFlag': serializer.toJson<int>(boundaryFlag),
      'gpsAccuracyFlag': serializer.toJson<int>(gpsAccuracyFlag),
      'qaFlags': serializer.toJson<String?>(qaFlags),
      'serverId': serializer.toJson<String?>(serverId),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'lastModifiedAt': serializer.toJson<int>(lastModifiedAt),
      'createdAt': serializer.toJson<int>(createdAt),
    };
  }

  Street copyWith(
          {int? id,
          String? streetId,
          String? streetName,
          String? streetAddress,
          String? streetType,
          String? surfaceType,
          String? streetCondition,
          Value<String?> notes = const Value.absent(),
          Uint8List? geometryWkb,
          Value<String?> zone = const Value.absent(),
          String? lga,
          Value<String?> ward = const Value.absent(),
          String? enumeratorId,
          int? enumerationDate,
          String? verificationStatus,
          int? boundaryFlag,
          int? gpsAccuracyFlag,
          Value<String?> qaFlags = const Value.absent(),
          Value<String?> serverId = const Value.absent(),
          String? syncStatus,
          int? lastModifiedAt,
          int? createdAt}) =>
      Street(
        id: id ?? this.id,
        streetId: streetId ?? this.streetId,
        streetName: streetName ?? this.streetName,
        streetAddress: streetAddress ?? this.streetAddress,
        streetType: streetType ?? this.streetType,
        surfaceType: surfaceType ?? this.surfaceType,
        streetCondition: streetCondition ?? this.streetCondition,
        notes: notes.present ? notes.value : this.notes,
        geometryWkb: geometryWkb ?? this.geometryWkb,
        zone: zone.present ? zone.value : this.zone,
        lga: lga ?? this.lga,
        ward: ward.present ? ward.value : this.ward,
        enumeratorId: enumeratorId ?? this.enumeratorId,
        enumerationDate: enumerationDate ?? this.enumerationDate,
        verificationStatus: verificationStatus ?? this.verificationStatus,
        boundaryFlag: boundaryFlag ?? this.boundaryFlag,
        gpsAccuracyFlag: gpsAccuracyFlag ?? this.gpsAccuracyFlag,
        qaFlags: qaFlags.present ? qaFlags.value : this.qaFlags,
        serverId: serverId.present ? serverId.value : this.serverId,
        syncStatus: syncStatus ?? this.syncStatus,
        lastModifiedAt: lastModifiedAt ?? this.lastModifiedAt,
        createdAt: createdAt ?? this.createdAt,
      );
  Street copyWithCompanion(StreetsCompanion data) {
    return Street(
      id: data.id.present ? data.id.value : this.id,
      streetId: data.streetId.present ? data.streetId.value : this.streetId,
      streetName:
          data.streetName.present ? data.streetName.value : this.streetName,
      streetAddress: data.streetAddress.present
          ? data.streetAddress.value
          : this.streetAddress,
      streetType:
          data.streetType.present ? data.streetType.value : this.streetType,
      surfaceType:
          data.surfaceType.present ? data.surfaceType.value : this.surfaceType,
      streetCondition: data.streetCondition.present
          ? data.streetCondition.value
          : this.streetCondition,
      notes: data.notes.present ? data.notes.value : this.notes,
      geometryWkb:
          data.geometryWkb.present ? data.geometryWkb.value : this.geometryWkb,
      zone: data.zone.present ? data.zone.value : this.zone,
      lga: data.lga.present ? data.lga.value : this.lga,
      ward: data.ward.present ? data.ward.value : this.ward,
      enumeratorId: data.enumeratorId.present
          ? data.enumeratorId.value
          : this.enumeratorId,
      enumerationDate: data.enumerationDate.present
          ? data.enumerationDate.value
          : this.enumerationDate,
      verificationStatus: data.verificationStatus.present
          ? data.verificationStatus.value
          : this.verificationStatus,
      boundaryFlag: data.boundaryFlag.present
          ? data.boundaryFlag.value
          : this.boundaryFlag,
      gpsAccuracyFlag: data.gpsAccuracyFlag.present
          ? data.gpsAccuracyFlag.value
          : this.gpsAccuracyFlag,
      qaFlags: data.qaFlags.present ? data.qaFlags.value : this.qaFlags,
      serverId: data.serverId.present ? data.serverId.value : this.serverId,
      syncStatus:
          data.syncStatus.present ? data.syncStatus.value : this.syncStatus,
      lastModifiedAt: data.lastModifiedAt.present
          ? data.lastModifiedAt.value
          : this.lastModifiedAt,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Street(')
          ..write('id: $id, ')
          ..write('streetId: $streetId, ')
          ..write('streetName: $streetName, ')
          ..write('streetAddress: $streetAddress, ')
          ..write('streetType: $streetType, ')
          ..write('surfaceType: $surfaceType, ')
          ..write('streetCondition: $streetCondition, ')
          ..write('notes: $notes, ')
          ..write('geometryWkb: $geometryWkb, ')
          ..write('zone: $zone, ')
          ..write('lga: $lga, ')
          ..write('ward: $ward, ')
          ..write('enumeratorId: $enumeratorId, ')
          ..write('enumerationDate: $enumerationDate, ')
          ..write('verificationStatus: $verificationStatus, ')
          ..write('boundaryFlag: $boundaryFlag, ')
          ..write('gpsAccuracyFlag: $gpsAccuracyFlag, ')
          ..write('qaFlags: $qaFlags, ')
          ..write('serverId: $serverId, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('lastModifiedAt: $lastModifiedAt, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hashAll([
        id,
        streetId,
        streetName,
        streetAddress,
        streetType,
        surfaceType,
        streetCondition,
        notes,
        $driftBlobEquality.hash(geometryWkb),
        zone,
        lga,
        ward,
        enumeratorId,
        enumerationDate,
        verificationStatus,
        boundaryFlag,
        gpsAccuracyFlag,
        qaFlags,
        serverId,
        syncStatus,
        lastModifiedAt,
        createdAt
      ]);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Street &&
          other.id == this.id &&
          other.streetId == this.streetId &&
          other.streetName == this.streetName &&
          other.streetAddress == this.streetAddress &&
          other.streetType == this.streetType &&
          other.surfaceType == this.surfaceType &&
          other.streetCondition == this.streetCondition &&
          other.notes == this.notes &&
          $driftBlobEquality.equals(other.geometryWkb, this.geometryWkb) &&
          other.zone == this.zone &&
          other.lga == this.lga &&
          other.ward == this.ward &&
          other.enumeratorId == this.enumeratorId &&
          other.enumerationDate == this.enumerationDate &&
          other.verificationStatus == this.verificationStatus &&
          other.boundaryFlag == this.boundaryFlag &&
          other.gpsAccuracyFlag == this.gpsAccuracyFlag &&
          other.qaFlags == this.qaFlags &&
          other.serverId == this.serverId &&
          other.syncStatus == this.syncStatus &&
          other.lastModifiedAt == this.lastModifiedAt &&
          other.createdAt == this.createdAt);
}

class StreetsCompanion extends UpdateCompanion<Street> {
  final Value<int> id;
  final Value<String> streetId;
  final Value<String> streetName;
  final Value<String> streetAddress;
  final Value<String> streetType;
  final Value<String> surfaceType;
  final Value<String> streetCondition;
  final Value<String?> notes;
  final Value<Uint8List> geometryWkb;
  final Value<String?> zone;
  final Value<String> lga;
  final Value<String?> ward;
  final Value<String> enumeratorId;
  final Value<int> enumerationDate;
  final Value<String> verificationStatus;
  final Value<int> boundaryFlag;
  final Value<int> gpsAccuracyFlag;
  final Value<String?> qaFlags;
  final Value<String?> serverId;
  final Value<String> syncStatus;
  final Value<int> lastModifiedAt;
  final Value<int> createdAt;
  const StreetsCompanion({
    this.id = const Value.absent(),
    this.streetId = const Value.absent(),
    this.streetName = const Value.absent(),
    this.streetAddress = const Value.absent(),
    this.streetType = const Value.absent(),
    this.surfaceType = const Value.absent(),
    this.streetCondition = const Value.absent(),
    this.notes = const Value.absent(),
    this.geometryWkb = const Value.absent(),
    this.zone = const Value.absent(),
    this.lga = const Value.absent(),
    this.ward = const Value.absent(),
    this.enumeratorId = const Value.absent(),
    this.enumerationDate = const Value.absent(),
    this.verificationStatus = const Value.absent(),
    this.boundaryFlag = const Value.absent(),
    this.gpsAccuracyFlag = const Value.absent(),
    this.qaFlags = const Value.absent(),
    this.serverId = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.lastModifiedAt = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  StreetsCompanion.insert({
    this.id = const Value.absent(),
    required String streetId,
    required String streetName,
    this.streetAddress = const Value.absent(),
    required String streetType,
    required String surfaceType,
    required String streetCondition,
    this.notes = const Value.absent(),
    required Uint8List geometryWkb,
    this.zone = const Value.absent(),
    required String lga,
    this.ward = const Value.absent(),
    required String enumeratorId,
    required int enumerationDate,
    this.verificationStatus = const Value.absent(),
    this.boundaryFlag = const Value.absent(),
    this.gpsAccuracyFlag = const Value.absent(),
    this.qaFlags = const Value.absent(),
    this.serverId = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.lastModifiedAt = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : streetId = Value(streetId),
        streetName = Value(streetName),
        streetType = Value(streetType),
        surfaceType = Value(surfaceType),
        streetCondition = Value(streetCondition),
        geometryWkb = Value(geometryWkb),
        lga = Value(lga),
        enumeratorId = Value(enumeratorId),
        enumerationDate = Value(enumerationDate);
  static Insertable<Street> custom({
    Expression<int>? id,
    Expression<String>? streetId,
    Expression<String>? streetName,
    Expression<String>? streetAddress,
    Expression<String>? streetType,
    Expression<String>? surfaceType,
    Expression<String>? streetCondition,
    Expression<String>? notes,
    Expression<Uint8List>? geometryWkb,
    Expression<String>? zone,
    Expression<String>? lga,
    Expression<String>? ward,
    Expression<String>? enumeratorId,
    Expression<int>? enumerationDate,
    Expression<String>? verificationStatus,
    Expression<int>? boundaryFlag,
    Expression<int>? gpsAccuracyFlag,
    Expression<String>? qaFlags,
    Expression<String>? serverId,
    Expression<String>? syncStatus,
    Expression<int>? lastModifiedAt,
    Expression<int>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (streetId != null) 'street_id': streetId,
      if (streetName != null) 'street_name': streetName,
      if (streetAddress != null) 'street_address': streetAddress,
      if (streetType != null) 'street_type': streetType,
      if (surfaceType != null) 'surface_type': surfaceType,
      if (streetCondition != null) 'street_condition': streetCondition,
      if (notes != null) 'notes': notes,
      if (geometryWkb != null) 'geometry_wkb': geometryWkb,
      if (zone != null) 'zone': zone,
      if (lga != null) 'lga': lga,
      if (ward != null) 'ward': ward,
      if (enumeratorId != null) 'enumerator_id': enumeratorId,
      if (enumerationDate != null) 'enumeration_date': enumerationDate,
      if (verificationStatus != null) 'verification_status': verificationStatus,
      if (boundaryFlag != null) 'boundary_flag': boundaryFlag,
      if (gpsAccuracyFlag != null) 'gps_accuracy_flag': gpsAccuracyFlag,
      if (qaFlags != null) 'qa_flags': qaFlags,
      if (serverId != null) 'server_id': serverId,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (lastModifiedAt != null) 'last_modified_at': lastModifiedAt,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  StreetsCompanion copyWith(
      {Value<int>? id,
      Value<String>? streetId,
      Value<String>? streetName,
      Value<String>? streetAddress,
      Value<String>? streetType,
      Value<String>? surfaceType,
      Value<String>? streetCondition,
      Value<String?>? notes,
      Value<Uint8List>? geometryWkb,
      Value<String?>? zone,
      Value<String>? lga,
      Value<String?>? ward,
      Value<String>? enumeratorId,
      Value<int>? enumerationDate,
      Value<String>? verificationStatus,
      Value<int>? boundaryFlag,
      Value<int>? gpsAccuracyFlag,
      Value<String?>? qaFlags,
      Value<String?>? serverId,
      Value<String>? syncStatus,
      Value<int>? lastModifiedAt,
      Value<int>? createdAt}) {
    return StreetsCompanion(
      id: id ?? this.id,
      streetId: streetId ?? this.streetId,
      streetName: streetName ?? this.streetName,
      streetAddress: streetAddress ?? this.streetAddress,
      streetType: streetType ?? this.streetType,
      surfaceType: surfaceType ?? this.surfaceType,
      streetCondition: streetCondition ?? this.streetCondition,
      notes: notes ?? this.notes,
      geometryWkb: geometryWkb ?? this.geometryWkb,
      zone: zone ?? this.zone,
      lga: lga ?? this.lga,
      ward: ward ?? this.ward,
      enumeratorId: enumeratorId ?? this.enumeratorId,
      enumerationDate: enumerationDate ?? this.enumerationDate,
      verificationStatus: verificationStatus ?? this.verificationStatus,
      boundaryFlag: boundaryFlag ?? this.boundaryFlag,
      gpsAccuracyFlag: gpsAccuracyFlag ?? this.gpsAccuracyFlag,
      qaFlags: qaFlags ?? this.qaFlags,
      serverId: serverId ?? this.serverId,
      syncStatus: syncStatus ?? this.syncStatus,
      lastModifiedAt: lastModifiedAt ?? this.lastModifiedAt,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (streetId.present) {
      map['street_id'] = Variable<String>(streetId.value);
    }
    if (streetName.present) {
      map['street_name'] = Variable<String>(streetName.value);
    }
    if (streetAddress.present) {
      map['street_address'] = Variable<String>(streetAddress.value);
    }
    if (streetType.present) {
      map['street_type'] = Variable<String>(streetType.value);
    }
    if (surfaceType.present) {
      map['surface_type'] = Variable<String>(surfaceType.value);
    }
    if (streetCondition.present) {
      map['street_condition'] = Variable<String>(streetCondition.value);
    }
    if (notes.present) {
      map['notes'] = Variable<String>(notes.value);
    }
    if (geometryWkb.present) {
      map['geometry_wkb'] = Variable<Uint8List>(geometryWkb.value);
    }
    if (zone.present) {
      map['zone'] = Variable<String>(zone.value);
    }
    if (lga.present) {
      map['lga'] = Variable<String>(lga.value);
    }
    if (ward.present) {
      map['ward'] = Variable<String>(ward.value);
    }
    if (enumeratorId.present) {
      map['enumerator_id'] = Variable<String>(enumeratorId.value);
    }
    if (enumerationDate.present) {
      map['enumeration_date'] = Variable<int>(enumerationDate.value);
    }
    if (verificationStatus.present) {
      map['verification_status'] = Variable<String>(verificationStatus.value);
    }
    if (boundaryFlag.present) {
      map['boundary_flag'] = Variable<int>(boundaryFlag.value);
    }
    if (gpsAccuracyFlag.present) {
      map['gps_accuracy_flag'] = Variable<int>(gpsAccuracyFlag.value);
    }
    if (qaFlags.present) {
      map['qa_flags'] = Variable<String>(qaFlags.value);
    }
    if (serverId.present) {
      map['server_id'] = Variable<String>(serverId.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (lastModifiedAt.present) {
      map['last_modified_at'] = Variable<int>(lastModifiedAt.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<int>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('StreetsCompanion(')
          ..write('id: $id, ')
          ..write('streetId: $streetId, ')
          ..write('streetName: $streetName, ')
          ..write('streetAddress: $streetAddress, ')
          ..write('streetType: $streetType, ')
          ..write('surfaceType: $surfaceType, ')
          ..write('streetCondition: $streetCondition, ')
          ..write('notes: $notes, ')
          ..write('geometryWkb: $geometryWkb, ')
          ..write('zone: $zone, ')
          ..write('lga: $lga, ')
          ..write('ward: $ward, ')
          ..write('enumeratorId: $enumeratorId, ')
          ..write('enumerationDate: $enumerationDate, ')
          ..write('verificationStatus: $verificationStatus, ')
          ..write('boundaryFlag: $boundaryFlag, ')
          ..write('gpsAccuracyFlag: $gpsAccuracyFlag, ')
          ..write('qaFlags: $qaFlags, ')
          ..write('serverId: $serverId, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('lastModifiedAt: $lastModifiedAt, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

class $BuildingsTable extends Buildings
    with TableInfo<$BuildingsTable, Building> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $BuildingsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _buildingIdMeta =
      const VerificationMeta('buildingId');
  @override
  late final GeneratedColumn<String> buildingId = GeneratedColumn<String>(
      'building_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways('UNIQUE'));
  static const VerificationMeta _streetIdMeta =
      const VerificationMeta('streetId');
  @override
  late final GeneratedColumn<String> streetId = GeneratedColumn<String>(
      'street_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _buildingTypeMeta =
      const VerificationMeta('buildingType');
  @override
  late final GeneratedColumn<String> buildingType = GeneratedColumn<String>(
      'building_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _numberOfFloorsMeta =
      const VerificationMeta('numberOfFloors');
  @override
  late final GeneratedColumn<int> numberOfFloors = GeneratedColumn<int>(
      'number_of_floors', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _numberOfUnitsMeta =
      const VerificationMeta('numberOfUnits');
  @override
  late final GeneratedColumn<int> numberOfUnits = GeneratedColumn<int>(
      'number_of_units', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _buildingConditionMeta =
      const VerificationMeta('buildingCondition');
  @override
  late final GeneratedColumn<String> buildingCondition =
      GeneratedColumn<String>('building_condition', aliasedName, false,
          type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _streetAddressMeta =
      const VerificationMeta('streetAddress');
  @override
  late final GeneratedColumn<String> streetAddress = GeneratedColumn<String>(
      'street_address', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _hasSignageMeta =
      const VerificationMeta('hasSignage');
  @override
  late final GeneratedColumn<int> hasSignage = GeneratedColumn<int>(
      'has_signage', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _businessNamesMeta =
      const VerificationMeta('businessNames');
  @override
  late final GeneratedColumn<String> businessNames = GeneratedColumn<String>(
      'business_names', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _notesMeta = const VerificationMeta('notes');
  @override
  late final GeneratedColumn<String> notes = GeneratedColumn<String>(
      'notes', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _geometryWkbMeta =
      const VerificationMeta('geometryWkb');
  @override
  late final GeneratedColumn<Uint8List> geometryWkb =
      GeneratedColumn<Uint8List>('geometry_wkb', aliasedName, false,
          type: DriftSqlType.blob, requiredDuringInsert: true);
  static const VerificationMeta _gpsAccuracyMMeta =
      const VerificationMeta('gpsAccuracyM');
  @override
  late final GeneratedColumn<double> gpsAccuracyM = GeneratedColumn<double>(
      'gps_accuracy_m', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _zoneMeta = const VerificationMeta('zone');
  @override
  late final GeneratedColumn<String> zone = GeneratedColumn<String>(
      'zone', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _lgaMeta = const VerificationMeta('lga');
  @override
  late final GeneratedColumn<String> lga = GeneratedColumn<String>(
      'lga', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _wardMeta = const VerificationMeta('ward');
  @override
  late final GeneratedColumn<String> ward = GeneratedColumn<String>(
      'ward', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _postcodeMeta =
      const VerificationMeta('postcode');
  @override
  late final GeneratedColumn<String> postcode = GeneratedColumn<String>(
      'postcode', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _postcodeStatusMeta =
      const VerificationMeta('postcodeStatus');
  @override
  late final GeneratedColumn<String> postcodeStatus = GeneratedColumn<String>(
      'postcode_status', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('resolved'));
  static const VerificationMeta _enumeratorIdMeta =
      const VerificationMeta('enumeratorId');
  @override
  late final GeneratedColumn<String> enumeratorId = GeneratedColumn<String>(
      'enumerator_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _enumerationDateMeta =
      const VerificationMeta('enumerationDate');
  @override
  late final GeneratedColumn<int> enumerationDate = GeneratedColumn<int>(
      'enumeration_date', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _verificationStatusMeta =
      const VerificationMeta('verificationStatus');
  @override
  late final GeneratedColumn<String> verificationStatus =
      GeneratedColumn<String>('verification_status', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: false,
          defaultValue: const Constant('pending'));
  static const VerificationMeta _rejectionReasonMeta =
      const VerificationMeta('rejectionReason');
  @override
  late final GeneratedColumn<String> rejectionReason = GeneratedColumn<String>(
      'rejection_reason', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _disputeReasonMeta =
      const VerificationMeta('disputeReason');
  @override
  late final GeneratedColumn<String> disputeReason = GeneratedColumn<String>(
      'dispute_reason', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _verifiedByMeta =
      const VerificationMeta('verifiedBy');
  @override
  late final GeneratedColumn<String> verifiedBy = GeneratedColumn<String>(
      'verified_by', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _verifiedAtMeta =
      const VerificationMeta('verifiedAt');
  @override
  late final GeneratedColumn<int> verifiedAt = GeneratedColumn<int>(
      'verified_at', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _boundaryFlagMeta =
      const VerificationMeta('boundaryFlag');
  @override
  late final GeneratedColumn<int> boundaryFlag = GeneratedColumn<int>(
      'boundary_flag', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _gpsAccuracyFlagMeta =
      const VerificationMeta('gpsAccuracyFlag');
  @override
  late final GeneratedColumn<int> gpsAccuracyFlag = GeneratedColumn<int>(
      'gps_accuracy_flag', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _duplicateFlagMeta =
      const VerificationMeta('duplicateFlag');
  @override
  late final GeneratedColumn<int> duplicateFlag = GeneratedColumn<int>(
      'duplicate_flag', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _qaFlagsMeta =
      const VerificationMeta('qaFlags');
  @override
  late final GeneratedColumn<String> qaFlags = GeneratedColumn<String>(
      'qa_flags', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _serverIdMeta =
      const VerificationMeta('serverId');
  @override
  late final GeneratedColumn<String> serverId = GeneratedColumn<String>(
      'server_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _syncStatusMeta =
      const VerificationMeta('syncStatus');
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
      'sync_status', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('queued'));
  static const VerificationMeta _lastModifiedAtMeta =
      const VerificationMeta('lastModifiedAt');
  @override
  late final GeneratedColumn<int> lastModifiedAt = GeneratedColumn<int>(
      'last_modified_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<int> createdAt = GeneratedColumn<int>(
      'created_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  @override
  List<GeneratedColumn> get $columns => [
        id,
        buildingId,
        streetId,
        buildingType,
        numberOfFloors,
        numberOfUnits,
        buildingCondition,
        streetAddress,
        hasSignage,
        businessNames,
        notes,
        geometryWkb,
        gpsAccuracyM,
        zone,
        lga,
        ward,
        postcode,
        postcodeStatus,
        enumeratorId,
        enumerationDate,
        verificationStatus,
        rejectionReason,
        disputeReason,
        verifiedBy,
        verifiedAt,
        boundaryFlag,
        gpsAccuracyFlag,
        duplicateFlag,
        qaFlags,
        serverId,
        syncStatus,
        lastModifiedAt,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'buildings';
  @override
  VerificationContext validateIntegrity(Insertable<Building> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('building_id')) {
      context.handle(
          _buildingIdMeta,
          buildingId.isAcceptableOrUnknown(
              data['building_id']!, _buildingIdMeta));
    } else if (isInserting) {
      context.missing(_buildingIdMeta);
    }
    if (data.containsKey('street_id')) {
      context.handle(_streetIdMeta,
          streetId.isAcceptableOrUnknown(data['street_id']!, _streetIdMeta));
    } else if (isInserting) {
      context.missing(_streetIdMeta);
    }
    if (data.containsKey('building_type')) {
      context.handle(
          _buildingTypeMeta,
          buildingType.isAcceptableOrUnknown(
              data['building_type']!, _buildingTypeMeta));
    } else if (isInserting) {
      context.missing(_buildingTypeMeta);
    }
    if (data.containsKey('number_of_floors')) {
      context.handle(
          _numberOfFloorsMeta,
          numberOfFloors.isAcceptableOrUnknown(
              data['number_of_floors']!, _numberOfFloorsMeta));
    } else if (isInserting) {
      context.missing(_numberOfFloorsMeta);
    }
    if (data.containsKey('number_of_units')) {
      context.handle(
          _numberOfUnitsMeta,
          numberOfUnits.isAcceptableOrUnknown(
              data['number_of_units']!, _numberOfUnitsMeta));
    } else if (isInserting) {
      context.missing(_numberOfUnitsMeta);
    }
    if (data.containsKey('building_condition')) {
      context.handle(
          _buildingConditionMeta,
          buildingCondition.isAcceptableOrUnknown(
              data['building_condition']!, _buildingConditionMeta));
    } else if (isInserting) {
      context.missing(_buildingConditionMeta);
    }
    if (data.containsKey('street_address')) {
      context.handle(
          _streetAddressMeta,
          streetAddress.isAcceptableOrUnknown(
              data['street_address']!, _streetAddressMeta));
    }
    if (data.containsKey('has_signage')) {
      context.handle(
          _hasSignageMeta,
          hasSignage.isAcceptableOrUnknown(
              data['has_signage']!, _hasSignageMeta));
    }
    if (data.containsKey('business_names')) {
      context.handle(
          _businessNamesMeta,
          businessNames.isAcceptableOrUnknown(
              data['business_names']!, _businessNamesMeta));
    }
    if (data.containsKey('notes')) {
      context.handle(
          _notesMeta, notes.isAcceptableOrUnknown(data['notes']!, _notesMeta));
    }
    if (data.containsKey('geometry_wkb')) {
      context.handle(
          _geometryWkbMeta,
          geometryWkb.isAcceptableOrUnknown(
              data['geometry_wkb']!, _geometryWkbMeta));
    } else if (isInserting) {
      context.missing(_geometryWkbMeta);
    }
    if (data.containsKey('gps_accuracy_m')) {
      context.handle(
          _gpsAccuracyMMeta,
          gpsAccuracyM.isAcceptableOrUnknown(
              data['gps_accuracy_m']!, _gpsAccuracyMMeta));
    } else if (isInserting) {
      context.missing(_gpsAccuracyMMeta);
    }
    if (data.containsKey('zone')) {
      context.handle(
          _zoneMeta, zone.isAcceptableOrUnknown(data['zone']!, _zoneMeta));
    }
    if (data.containsKey('lga')) {
      context.handle(
          _lgaMeta, lga.isAcceptableOrUnknown(data['lga']!, _lgaMeta));
    } else if (isInserting) {
      context.missing(_lgaMeta);
    }
    if (data.containsKey('ward')) {
      context.handle(
          _wardMeta, ward.isAcceptableOrUnknown(data['ward']!, _wardMeta));
    }
    if (data.containsKey('postcode')) {
      context.handle(_postcodeMeta,
          postcode.isAcceptableOrUnknown(data['postcode']!, _postcodeMeta));
    }
    if (data.containsKey('postcode_status')) {
      context.handle(
          _postcodeStatusMeta,
          postcodeStatus.isAcceptableOrUnknown(
              data['postcode_status']!, _postcodeStatusMeta));
    }
    if (data.containsKey('enumerator_id')) {
      context.handle(
          _enumeratorIdMeta,
          enumeratorId.isAcceptableOrUnknown(
              data['enumerator_id']!, _enumeratorIdMeta));
    } else if (isInserting) {
      context.missing(_enumeratorIdMeta);
    }
    if (data.containsKey('enumeration_date')) {
      context.handle(
          _enumerationDateMeta,
          enumerationDate.isAcceptableOrUnknown(
              data['enumeration_date']!, _enumerationDateMeta));
    } else if (isInserting) {
      context.missing(_enumerationDateMeta);
    }
    if (data.containsKey('verification_status')) {
      context.handle(
          _verificationStatusMeta,
          verificationStatus.isAcceptableOrUnknown(
              data['verification_status']!, _verificationStatusMeta));
    }
    if (data.containsKey('rejection_reason')) {
      context.handle(
          _rejectionReasonMeta,
          rejectionReason.isAcceptableOrUnknown(
              data['rejection_reason']!, _rejectionReasonMeta));
    }
    if (data.containsKey('dispute_reason')) {
      context.handle(
          _disputeReasonMeta,
          disputeReason.isAcceptableOrUnknown(
              data['dispute_reason']!, _disputeReasonMeta));
    }
    if (data.containsKey('verified_by')) {
      context.handle(
          _verifiedByMeta,
          verifiedBy.isAcceptableOrUnknown(
              data['verified_by']!, _verifiedByMeta));
    }
    if (data.containsKey('verified_at')) {
      context.handle(
          _verifiedAtMeta,
          verifiedAt.isAcceptableOrUnknown(
              data['verified_at']!, _verifiedAtMeta));
    }
    if (data.containsKey('boundary_flag')) {
      context.handle(
          _boundaryFlagMeta,
          boundaryFlag.isAcceptableOrUnknown(
              data['boundary_flag']!, _boundaryFlagMeta));
    }
    if (data.containsKey('gps_accuracy_flag')) {
      context.handle(
          _gpsAccuracyFlagMeta,
          gpsAccuracyFlag.isAcceptableOrUnknown(
              data['gps_accuracy_flag']!, _gpsAccuracyFlagMeta));
    }
    if (data.containsKey('duplicate_flag')) {
      context.handle(
          _duplicateFlagMeta,
          duplicateFlag.isAcceptableOrUnknown(
              data['duplicate_flag']!, _duplicateFlagMeta));
    }
    if (data.containsKey('qa_flags')) {
      context.handle(_qaFlagsMeta,
          qaFlags.isAcceptableOrUnknown(data['qa_flags']!, _qaFlagsMeta));
    }
    if (data.containsKey('server_id')) {
      context.handle(_serverIdMeta,
          serverId.isAcceptableOrUnknown(data['server_id']!, _serverIdMeta));
    }
    if (data.containsKey('sync_status')) {
      context.handle(
          _syncStatusMeta,
          syncStatus.isAcceptableOrUnknown(
              data['sync_status']!, _syncStatusMeta));
    }
    if (data.containsKey('last_modified_at')) {
      context.handle(
          _lastModifiedAtMeta,
          lastModifiedAt.isAcceptableOrUnknown(
              data['last_modified_at']!, _lastModifiedAtMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Building map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Building(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      buildingId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}building_id'])!,
      streetId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}street_id'])!,
      buildingType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}building_type'])!,
      numberOfFloors: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}number_of_floors'])!,
      numberOfUnits: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}number_of_units'])!,
      buildingCondition: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}building_condition'])!,
      streetAddress: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}street_address']),
      hasSignage: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}has_signage'])!,
      businessNames: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}business_names']),
      notes: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}notes']),
      geometryWkb: attachedDatabase.typeMapping
          .read(DriftSqlType.blob, data['${effectivePrefix}geometry_wkb'])!,
      gpsAccuracyM: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}gps_accuracy_m'])!,
      zone: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}zone']),
      lga: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}lga'])!,
      ward: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}ward']),
      postcode: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}postcode']),
      postcodeStatus: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}postcode_status'])!,
      enumeratorId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}enumerator_id'])!,
      enumerationDate: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}enumeration_date'])!,
      verificationStatus: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}verification_status'])!,
      rejectionReason: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}rejection_reason']),
      disputeReason: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}dispute_reason']),
      verifiedBy: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}verified_by']),
      verifiedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}verified_at']),
      boundaryFlag: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}boundary_flag'])!,
      gpsAccuracyFlag: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}gps_accuracy_flag'])!,
      duplicateFlag: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}duplicate_flag'])!,
      qaFlags: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}qa_flags']),
      serverId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}server_id']),
      syncStatus: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}sync_status'])!,
      lastModifiedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}last_modified_at'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $BuildingsTable createAlias(String alias) {
    return $BuildingsTable(attachedDatabase, alias);
  }
}

class Building extends DataClass implements Insertable<Building> {
  final int id;
  final String buildingId;
  final String streetId;
  final String buildingType;
  final int numberOfFloors;
  final int numberOfUnits;
  final String buildingCondition;
  final String? streetAddress;
  final int hasSignage;
  final String? businessNames;
  final String? notes;
  final Uint8List geometryWkb;
  final double gpsAccuracyM;
  final String? zone;
  final String lga;
  final String? ward;
  final String? postcode;
  final String postcodeStatus;
  final String enumeratorId;
  final int enumerationDate;
  final String verificationStatus;
  final String? rejectionReason;
  final String? disputeReason;
  final String? verifiedBy;
  final int? verifiedAt;
  final int boundaryFlag;
  final int gpsAccuracyFlag;
  final int duplicateFlag;
  final String? qaFlags;
  final String? serverId;
  final String syncStatus;
  final int lastModifiedAt;
  final int createdAt;
  const Building(
      {required this.id,
      required this.buildingId,
      required this.streetId,
      required this.buildingType,
      required this.numberOfFloors,
      required this.numberOfUnits,
      required this.buildingCondition,
      this.streetAddress,
      required this.hasSignage,
      this.businessNames,
      this.notes,
      required this.geometryWkb,
      required this.gpsAccuracyM,
      this.zone,
      required this.lga,
      this.ward,
      this.postcode,
      required this.postcodeStatus,
      required this.enumeratorId,
      required this.enumerationDate,
      required this.verificationStatus,
      this.rejectionReason,
      this.disputeReason,
      this.verifiedBy,
      this.verifiedAt,
      required this.boundaryFlag,
      required this.gpsAccuracyFlag,
      required this.duplicateFlag,
      this.qaFlags,
      this.serverId,
      required this.syncStatus,
      required this.lastModifiedAt,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['building_id'] = Variable<String>(buildingId);
    map['street_id'] = Variable<String>(streetId);
    map['building_type'] = Variable<String>(buildingType);
    map['number_of_floors'] = Variable<int>(numberOfFloors);
    map['number_of_units'] = Variable<int>(numberOfUnits);
    map['building_condition'] = Variable<String>(buildingCondition);
    if (!nullToAbsent || streetAddress != null) {
      map['street_address'] = Variable<String>(streetAddress);
    }
    map['has_signage'] = Variable<int>(hasSignage);
    if (!nullToAbsent || businessNames != null) {
      map['business_names'] = Variable<String>(businessNames);
    }
    if (!nullToAbsent || notes != null) {
      map['notes'] = Variable<String>(notes);
    }
    map['geometry_wkb'] = Variable<Uint8List>(geometryWkb);
    map['gps_accuracy_m'] = Variable<double>(gpsAccuracyM);
    if (!nullToAbsent || zone != null) {
      map['zone'] = Variable<String>(zone);
    }
    map['lga'] = Variable<String>(lga);
    if (!nullToAbsent || ward != null) {
      map['ward'] = Variable<String>(ward);
    }
    if (!nullToAbsent || postcode != null) {
      map['postcode'] = Variable<String>(postcode);
    }
    map['postcode_status'] = Variable<String>(postcodeStatus);
    map['enumerator_id'] = Variable<String>(enumeratorId);
    map['enumeration_date'] = Variable<int>(enumerationDate);
    map['verification_status'] = Variable<String>(verificationStatus);
    if (!nullToAbsent || rejectionReason != null) {
      map['rejection_reason'] = Variable<String>(rejectionReason);
    }
    if (!nullToAbsent || disputeReason != null) {
      map['dispute_reason'] = Variable<String>(disputeReason);
    }
    if (!nullToAbsent || verifiedBy != null) {
      map['verified_by'] = Variable<String>(verifiedBy);
    }
    if (!nullToAbsent || verifiedAt != null) {
      map['verified_at'] = Variable<int>(verifiedAt);
    }
    map['boundary_flag'] = Variable<int>(boundaryFlag);
    map['gps_accuracy_flag'] = Variable<int>(gpsAccuracyFlag);
    map['duplicate_flag'] = Variable<int>(duplicateFlag);
    if (!nullToAbsent || qaFlags != null) {
      map['qa_flags'] = Variable<String>(qaFlags);
    }
    if (!nullToAbsent || serverId != null) {
      map['server_id'] = Variable<String>(serverId);
    }
    map['sync_status'] = Variable<String>(syncStatus);
    map['last_modified_at'] = Variable<int>(lastModifiedAt);
    map['created_at'] = Variable<int>(createdAt);
    return map;
  }

  BuildingsCompanion toCompanion(bool nullToAbsent) {
    return BuildingsCompanion(
      id: Value(id),
      buildingId: Value(buildingId),
      streetId: Value(streetId),
      buildingType: Value(buildingType),
      numberOfFloors: Value(numberOfFloors),
      numberOfUnits: Value(numberOfUnits),
      buildingCondition: Value(buildingCondition),
      streetAddress: streetAddress == null && nullToAbsent
          ? const Value.absent()
          : Value(streetAddress),
      hasSignage: Value(hasSignage),
      businessNames: businessNames == null && nullToAbsent
          ? const Value.absent()
          : Value(businessNames),
      notes:
          notes == null && nullToAbsent ? const Value.absent() : Value(notes),
      geometryWkb: Value(geometryWkb),
      gpsAccuracyM: Value(gpsAccuracyM),
      zone: zone == null && nullToAbsent ? const Value.absent() : Value(zone),
      lga: Value(lga),
      ward: ward == null && nullToAbsent ? const Value.absent() : Value(ward),
      postcode: postcode == null && nullToAbsent
          ? const Value.absent()
          : Value(postcode),
      postcodeStatus: Value(postcodeStatus),
      enumeratorId: Value(enumeratorId),
      enumerationDate: Value(enumerationDate),
      verificationStatus: Value(verificationStatus),
      rejectionReason: rejectionReason == null && nullToAbsent
          ? const Value.absent()
          : Value(rejectionReason),
      disputeReason: disputeReason == null && nullToAbsent
          ? const Value.absent()
          : Value(disputeReason),
      verifiedBy: verifiedBy == null && nullToAbsent
          ? const Value.absent()
          : Value(verifiedBy),
      verifiedAt: verifiedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(verifiedAt),
      boundaryFlag: Value(boundaryFlag),
      gpsAccuracyFlag: Value(gpsAccuracyFlag),
      duplicateFlag: Value(duplicateFlag),
      qaFlags: qaFlags == null && nullToAbsent
          ? const Value.absent()
          : Value(qaFlags),
      serverId: serverId == null && nullToAbsent
          ? const Value.absent()
          : Value(serverId),
      syncStatus: Value(syncStatus),
      lastModifiedAt: Value(lastModifiedAt),
      createdAt: Value(createdAt),
    );
  }

  factory Building.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Building(
      id: serializer.fromJson<int>(json['id']),
      buildingId: serializer.fromJson<String>(json['buildingId']),
      streetId: serializer.fromJson<String>(json['streetId']),
      buildingType: serializer.fromJson<String>(json['buildingType']),
      numberOfFloors: serializer.fromJson<int>(json['numberOfFloors']),
      numberOfUnits: serializer.fromJson<int>(json['numberOfUnits']),
      buildingCondition: serializer.fromJson<String>(json['buildingCondition']),
      streetAddress: serializer.fromJson<String?>(json['streetAddress']),
      hasSignage: serializer.fromJson<int>(json['hasSignage']),
      businessNames: serializer.fromJson<String?>(json['businessNames']),
      notes: serializer.fromJson<String?>(json['notes']),
      geometryWkb: serializer.fromJson<Uint8List>(json['geometryWkb']),
      gpsAccuracyM: serializer.fromJson<double>(json['gpsAccuracyM']),
      zone: serializer.fromJson<String?>(json['zone']),
      lga: serializer.fromJson<String>(json['lga']),
      ward: serializer.fromJson<String?>(json['ward']),
      postcode: serializer.fromJson<String?>(json['postcode']),
      postcodeStatus: serializer.fromJson<String>(json['postcodeStatus']),
      enumeratorId: serializer.fromJson<String>(json['enumeratorId']),
      enumerationDate: serializer.fromJson<int>(json['enumerationDate']),
      verificationStatus:
          serializer.fromJson<String>(json['verificationStatus']),
      rejectionReason: serializer.fromJson<String?>(json['rejectionReason']),
      disputeReason: serializer.fromJson<String?>(json['disputeReason']),
      verifiedBy: serializer.fromJson<String?>(json['verifiedBy']),
      verifiedAt: serializer.fromJson<int?>(json['verifiedAt']),
      boundaryFlag: serializer.fromJson<int>(json['boundaryFlag']),
      gpsAccuracyFlag: serializer.fromJson<int>(json['gpsAccuracyFlag']),
      duplicateFlag: serializer.fromJson<int>(json['duplicateFlag']),
      qaFlags: serializer.fromJson<String?>(json['qaFlags']),
      serverId: serializer.fromJson<String?>(json['serverId']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      lastModifiedAt: serializer.fromJson<int>(json['lastModifiedAt']),
      createdAt: serializer.fromJson<int>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'buildingId': serializer.toJson<String>(buildingId),
      'streetId': serializer.toJson<String>(streetId),
      'buildingType': serializer.toJson<String>(buildingType),
      'numberOfFloors': serializer.toJson<int>(numberOfFloors),
      'numberOfUnits': serializer.toJson<int>(numberOfUnits),
      'buildingCondition': serializer.toJson<String>(buildingCondition),
      'streetAddress': serializer.toJson<String?>(streetAddress),
      'hasSignage': serializer.toJson<int>(hasSignage),
      'businessNames': serializer.toJson<String?>(businessNames),
      'notes': serializer.toJson<String?>(notes),
      'geometryWkb': serializer.toJson<Uint8List>(geometryWkb),
      'gpsAccuracyM': serializer.toJson<double>(gpsAccuracyM),
      'zone': serializer.toJson<String?>(zone),
      'lga': serializer.toJson<String>(lga),
      'ward': serializer.toJson<String?>(ward),
      'postcode': serializer.toJson<String?>(postcode),
      'postcodeStatus': serializer.toJson<String>(postcodeStatus),
      'enumeratorId': serializer.toJson<String>(enumeratorId),
      'enumerationDate': serializer.toJson<int>(enumerationDate),
      'verificationStatus': serializer.toJson<String>(verificationStatus),
      'rejectionReason': serializer.toJson<String?>(rejectionReason),
      'disputeReason': serializer.toJson<String?>(disputeReason),
      'verifiedBy': serializer.toJson<String?>(verifiedBy),
      'verifiedAt': serializer.toJson<int?>(verifiedAt),
      'boundaryFlag': serializer.toJson<int>(boundaryFlag),
      'gpsAccuracyFlag': serializer.toJson<int>(gpsAccuracyFlag),
      'duplicateFlag': serializer.toJson<int>(duplicateFlag),
      'qaFlags': serializer.toJson<String?>(qaFlags),
      'serverId': serializer.toJson<String?>(serverId),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'lastModifiedAt': serializer.toJson<int>(lastModifiedAt),
      'createdAt': serializer.toJson<int>(createdAt),
    };
  }

  Building copyWith(
          {int? id,
          String? buildingId,
          String? streetId,
          String? buildingType,
          int? numberOfFloors,
          int? numberOfUnits,
          String? buildingCondition,
          Value<String?> streetAddress = const Value.absent(),
          int? hasSignage,
          Value<String?> businessNames = const Value.absent(),
          Value<String?> notes = const Value.absent(),
          Uint8List? geometryWkb,
          double? gpsAccuracyM,
          Value<String?> zone = const Value.absent(),
          String? lga,
          Value<String?> ward = const Value.absent(),
          Value<String?> postcode = const Value.absent(),
          String? postcodeStatus,
          String? enumeratorId,
          int? enumerationDate,
          String? verificationStatus,
          Value<String?> rejectionReason = const Value.absent(),
          Value<String?> disputeReason = const Value.absent(),
          Value<String?> verifiedBy = const Value.absent(),
          Value<int?> verifiedAt = const Value.absent(),
          int? boundaryFlag,
          int? gpsAccuracyFlag,
          int? duplicateFlag,
          Value<String?> qaFlags = const Value.absent(),
          Value<String?> serverId = const Value.absent(),
          String? syncStatus,
          int? lastModifiedAt,
          int? createdAt}) =>
      Building(
        id: id ?? this.id,
        buildingId: buildingId ?? this.buildingId,
        streetId: streetId ?? this.streetId,
        buildingType: buildingType ?? this.buildingType,
        numberOfFloors: numberOfFloors ?? this.numberOfFloors,
        numberOfUnits: numberOfUnits ?? this.numberOfUnits,
        buildingCondition: buildingCondition ?? this.buildingCondition,
        streetAddress:
            streetAddress.present ? streetAddress.value : this.streetAddress,
        hasSignage: hasSignage ?? this.hasSignage,
        businessNames:
            businessNames.present ? businessNames.value : this.businessNames,
        notes: notes.present ? notes.value : this.notes,
        geometryWkb: geometryWkb ?? this.geometryWkb,
        gpsAccuracyM: gpsAccuracyM ?? this.gpsAccuracyM,
        zone: zone.present ? zone.value : this.zone,
        lga: lga ?? this.lga,
        ward: ward.present ? ward.value : this.ward,
        postcode: postcode.present ? postcode.value : this.postcode,
        postcodeStatus: postcodeStatus ?? this.postcodeStatus,
        enumeratorId: enumeratorId ?? this.enumeratorId,
        enumerationDate: enumerationDate ?? this.enumerationDate,
        verificationStatus: verificationStatus ?? this.verificationStatus,
        rejectionReason: rejectionReason.present
            ? rejectionReason.value
            : this.rejectionReason,
        disputeReason:
            disputeReason.present ? disputeReason.value : this.disputeReason,
        verifiedBy: verifiedBy.present ? verifiedBy.value : this.verifiedBy,
        verifiedAt: verifiedAt.present ? verifiedAt.value : this.verifiedAt,
        boundaryFlag: boundaryFlag ?? this.boundaryFlag,
        gpsAccuracyFlag: gpsAccuracyFlag ?? this.gpsAccuracyFlag,
        duplicateFlag: duplicateFlag ?? this.duplicateFlag,
        qaFlags: qaFlags.present ? qaFlags.value : this.qaFlags,
        serverId: serverId.present ? serverId.value : this.serverId,
        syncStatus: syncStatus ?? this.syncStatus,
        lastModifiedAt: lastModifiedAt ?? this.lastModifiedAt,
        createdAt: createdAt ?? this.createdAt,
      );
  Building copyWithCompanion(BuildingsCompanion data) {
    return Building(
      id: data.id.present ? data.id.value : this.id,
      buildingId:
          data.buildingId.present ? data.buildingId.value : this.buildingId,
      streetId: data.streetId.present ? data.streetId.value : this.streetId,
      buildingType: data.buildingType.present
          ? data.buildingType.value
          : this.buildingType,
      numberOfFloors: data.numberOfFloors.present
          ? data.numberOfFloors.value
          : this.numberOfFloors,
      numberOfUnits: data.numberOfUnits.present
          ? data.numberOfUnits.value
          : this.numberOfUnits,
      buildingCondition: data.buildingCondition.present
          ? data.buildingCondition.value
          : this.buildingCondition,
      streetAddress: data.streetAddress.present
          ? data.streetAddress.value
          : this.streetAddress,
      hasSignage:
          data.hasSignage.present ? data.hasSignage.value : this.hasSignage,
      businessNames: data.businessNames.present
          ? data.businessNames.value
          : this.businessNames,
      notes: data.notes.present ? data.notes.value : this.notes,
      geometryWkb:
          data.geometryWkb.present ? data.geometryWkb.value : this.geometryWkb,
      gpsAccuracyM: data.gpsAccuracyM.present
          ? data.gpsAccuracyM.value
          : this.gpsAccuracyM,
      zone: data.zone.present ? data.zone.value : this.zone,
      lga: data.lga.present ? data.lga.value : this.lga,
      ward: data.ward.present ? data.ward.value : this.ward,
      postcode: data.postcode.present ? data.postcode.value : this.postcode,
      postcodeStatus: data.postcodeStatus.present
          ? data.postcodeStatus.value
          : this.postcodeStatus,
      enumeratorId: data.enumeratorId.present
          ? data.enumeratorId.value
          : this.enumeratorId,
      enumerationDate: data.enumerationDate.present
          ? data.enumerationDate.value
          : this.enumerationDate,
      verificationStatus: data.verificationStatus.present
          ? data.verificationStatus.value
          : this.verificationStatus,
      rejectionReason: data.rejectionReason.present
          ? data.rejectionReason.value
          : this.rejectionReason,
      disputeReason: data.disputeReason.present
          ? data.disputeReason.value
          : this.disputeReason,
      verifiedBy:
          data.verifiedBy.present ? data.verifiedBy.value : this.verifiedBy,
      verifiedAt:
          data.verifiedAt.present ? data.verifiedAt.value : this.verifiedAt,
      boundaryFlag: data.boundaryFlag.present
          ? data.boundaryFlag.value
          : this.boundaryFlag,
      gpsAccuracyFlag: data.gpsAccuracyFlag.present
          ? data.gpsAccuracyFlag.value
          : this.gpsAccuracyFlag,
      duplicateFlag: data.duplicateFlag.present
          ? data.duplicateFlag.value
          : this.duplicateFlag,
      qaFlags: data.qaFlags.present ? data.qaFlags.value : this.qaFlags,
      serverId: data.serverId.present ? data.serverId.value : this.serverId,
      syncStatus:
          data.syncStatus.present ? data.syncStatus.value : this.syncStatus,
      lastModifiedAt: data.lastModifiedAt.present
          ? data.lastModifiedAt.value
          : this.lastModifiedAt,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Building(')
          ..write('id: $id, ')
          ..write('buildingId: $buildingId, ')
          ..write('streetId: $streetId, ')
          ..write('buildingType: $buildingType, ')
          ..write('numberOfFloors: $numberOfFloors, ')
          ..write('numberOfUnits: $numberOfUnits, ')
          ..write('buildingCondition: $buildingCondition, ')
          ..write('streetAddress: $streetAddress, ')
          ..write('hasSignage: $hasSignage, ')
          ..write('businessNames: $businessNames, ')
          ..write('notes: $notes, ')
          ..write('geometryWkb: $geometryWkb, ')
          ..write('gpsAccuracyM: $gpsAccuracyM, ')
          ..write('zone: $zone, ')
          ..write('lga: $lga, ')
          ..write('ward: $ward, ')
          ..write('postcode: $postcode, ')
          ..write('postcodeStatus: $postcodeStatus, ')
          ..write('enumeratorId: $enumeratorId, ')
          ..write('enumerationDate: $enumerationDate, ')
          ..write('verificationStatus: $verificationStatus, ')
          ..write('rejectionReason: $rejectionReason, ')
          ..write('disputeReason: $disputeReason, ')
          ..write('verifiedBy: $verifiedBy, ')
          ..write('verifiedAt: $verifiedAt, ')
          ..write('boundaryFlag: $boundaryFlag, ')
          ..write('gpsAccuracyFlag: $gpsAccuracyFlag, ')
          ..write('duplicateFlag: $duplicateFlag, ')
          ..write('qaFlags: $qaFlags, ')
          ..write('serverId: $serverId, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('lastModifiedAt: $lastModifiedAt, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hashAll([
        id,
        buildingId,
        streetId,
        buildingType,
        numberOfFloors,
        numberOfUnits,
        buildingCondition,
        streetAddress,
        hasSignage,
        businessNames,
        notes,
        $driftBlobEquality.hash(geometryWkb),
        gpsAccuracyM,
        zone,
        lga,
        ward,
        postcode,
        postcodeStatus,
        enumeratorId,
        enumerationDate,
        verificationStatus,
        rejectionReason,
        disputeReason,
        verifiedBy,
        verifiedAt,
        boundaryFlag,
        gpsAccuracyFlag,
        duplicateFlag,
        qaFlags,
        serverId,
        syncStatus,
        lastModifiedAt,
        createdAt
      ]);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Building &&
          other.id == this.id &&
          other.buildingId == this.buildingId &&
          other.streetId == this.streetId &&
          other.buildingType == this.buildingType &&
          other.numberOfFloors == this.numberOfFloors &&
          other.numberOfUnits == this.numberOfUnits &&
          other.buildingCondition == this.buildingCondition &&
          other.streetAddress == this.streetAddress &&
          other.hasSignage == this.hasSignage &&
          other.businessNames == this.businessNames &&
          other.notes == this.notes &&
          $driftBlobEquality.equals(other.geometryWkb, this.geometryWkb) &&
          other.gpsAccuracyM == this.gpsAccuracyM &&
          other.zone == this.zone &&
          other.lga == this.lga &&
          other.ward == this.ward &&
          other.postcode == this.postcode &&
          other.postcodeStatus == this.postcodeStatus &&
          other.enumeratorId == this.enumeratorId &&
          other.enumerationDate == this.enumerationDate &&
          other.verificationStatus == this.verificationStatus &&
          other.rejectionReason == this.rejectionReason &&
          other.disputeReason == this.disputeReason &&
          other.verifiedBy == this.verifiedBy &&
          other.verifiedAt == this.verifiedAt &&
          other.boundaryFlag == this.boundaryFlag &&
          other.gpsAccuracyFlag == this.gpsAccuracyFlag &&
          other.duplicateFlag == this.duplicateFlag &&
          other.qaFlags == this.qaFlags &&
          other.serverId == this.serverId &&
          other.syncStatus == this.syncStatus &&
          other.lastModifiedAt == this.lastModifiedAt &&
          other.createdAt == this.createdAt);
}

class BuildingsCompanion extends UpdateCompanion<Building> {
  final Value<int> id;
  final Value<String> buildingId;
  final Value<String> streetId;
  final Value<String> buildingType;
  final Value<int> numberOfFloors;
  final Value<int> numberOfUnits;
  final Value<String> buildingCondition;
  final Value<String?> streetAddress;
  final Value<int> hasSignage;
  final Value<String?> businessNames;
  final Value<String?> notes;
  final Value<Uint8List> geometryWkb;
  final Value<double> gpsAccuracyM;
  final Value<String?> zone;
  final Value<String> lga;
  final Value<String?> ward;
  final Value<String?> postcode;
  final Value<String> postcodeStatus;
  final Value<String> enumeratorId;
  final Value<int> enumerationDate;
  final Value<String> verificationStatus;
  final Value<String?> rejectionReason;
  final Value<String?> disputeReason;
  final Value<String?> verifiedBy;
  final Value<int?> verifiedAt;
  final Value<int> boundaryFlag;
  final Value<int> gpsAccuracyFlag;
  final Value<int> duplicateFlag;
  final Value<String?> qaFlags;
  final Value<String?> serverId;
  final Value<String> syncStatus;
  final Value<int> lastModifiedAt;
  final Value<int> createdAt;
  const BuildingsCompanion({
    this.id = const Value.absent(),
    this.buildingId = const Value.absent(),
    this.streetId = const Value.absent(),
    this.buildingType = const Value.absent(),
    this.numberOfFloors = const Value.absent(),
    this.numberOfUnits = const Value.absent(),
    this.buildingCondition = const Value.absent(),
    this.streetAddress = const Value.absent(),
    this.hasSignage = const Value.absent(),
    this.businessNames = const Value.absent(),
    this.notes = const Value.absent(),
    this.geometryWkb = const Value.absent(),
    this.gpsAccuracyM = const Value.absent(),
    this.zone = const Value.absent(),
    this.lga = const Value.absent(),
    this.ward = const Value.absent(),
    this.postcode = const Value.absent(),
    this.postcodeStatus = const Value.absent(),
    this.enumeratorId = const Value.absent(),
    this.enumerationDate = const Value.absent(),
    this.verificationStatus = const Value.absent(),
    this.rejectionReason = const Value.absent(),
    this.disputeReason = const Value.absent(),
    this.verifiedBy = const Value.absent(),
    this.verifiedAt = const Value.absent(),
    this.boundaryFlag = const Value.absent(),
    this.gpsAccuracyFlag = const Value.absent(),
    this.duplicateFlag = const Value.absent(),
    this.qaFlags = const Value.absent(),
    this.serverId = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.lastModifiedAt = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  BuildingsCompanion.insert({
    this.id = const Value.absent(),
    required String buildingId,
    required String streetId,
    required String buildingType,
    required int numberOfFloors,
    required int numberOfUnits,
    required String buildingCondition,
    this.streetAddress = const Value.absent(),
    this.hasSignage = const Value.absent(),
    this.businessNames = const Value.absent(),
    this.notes = const Value.absent(),
    required Uint8List geometryWkb,
    required double gpsAccuracyM,
    this.zone = const Value.absent(),
    required String lga,
    this.ward = const Value.absent(),
    this.postcode = const Value.absent(),
    this.postcodeStatus = const Value.absent(),
    required String enumeratorId,
    required int enumerationDate,
    this.verificationStatus = const Value.absent(),
    this.rejectionReason = const Value.absent(),
    this.disputeReason = const Value.absent(),
    this.verifiedBy = const Value.absent(),
    this.verifiedAt = const Value.absent(),
    this.boundaryFlag = const Value.absent(),
    this.gpsAccuracyFlag = const Value.absent(),
    this.duplicateFlag = const Value.absent(),
    this.qaFlags = const Value.absent(),
    this.serverId = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.lastModifiedAt = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : buildingId = Value(buildingId),
        streetId = Value(streetId),
        buildingType = Value(buildingType),
        numberOfFloors = Value(numberOfFloors),
        numberOfUnits = Value(numberOfUnits),
        buildingCondition = Value(buildingCondition),
        geometryWkb = Value(geometryWkb),
        gpsAccuracyM = Value(gpsAccuracyM),
        lga = Value(lga),
        enumeratorId = Value(enumeratorId),
        enumerationDate = Value(enumerationDate);
  static Insertable<Building> custom({
    Expression<int>? id,
    Expression<String>? buildingId,
    Expression<String>? streetId,
    Expression<String>? buildingType,
    Expression<int>? numberOfFloors,
    Expression<int>? numberOfUnits,
    Expression<String>? buildingCondition,
    Expression<String>? streetAddress,
    Expression<int>? hasSignage,
    Expression<String>? businessNames,
    Expression<String>? notes,
    Expression<Uint8List>? geometryWkb,
    Expression<double>? gpsAccuracyM,
    Expression<String>? zone,
    Expression<String>? lga,
    Expression<String>? ward,
    Expression<String>? postcode,
    Expression<String>? postcodeStatus,
    Expression<String>? enumeratorId,
    Expression<int>? enumerationDate,
    Expression<String>? verificationStatus,
    Expression<String>? rejectionReason,
    Expression<String>? disputeReason,
    Expression<String>? verifiedBy,
    Expression<int>? verifiedAt,
    Expression<int>? boundaryFlag,
    Expression<int>? gpsAccuracyFlag,
    Expression<int>? duplicateFlag,
    Expression<String>? qaFlags,
    Expression<String>? serverId,
    Expression<String>? syncStatus,
    Expression<int>? lastModifiedAt,
    Expression<int>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (buildingId != null) 'building_id': buildingId,
      if (streetId != null) 'street_id': streetId,
      if (buildingType != null) 'building_type': buildingType,
      if (numberOfFloors != null) 'number_of_floors': numberOfFloors,
      if (numberOfUnits != null) 'number_of_units': numberOfUnits,
      if (buildingCondition != null) 'building_condition': buildingCondition,
      if (streetAddress != null) 'street_address': streetAddress,
      if (hasSignage != null) 'has_signage': hasSignage,
      if (businessNames != null) 'business_names': businessNames,
      if (notes != null) 'notes': notes,
      if (geometryWkb != null) 'geometry_wkb': geometryWkb,
      if (gpsAccuracyM != null) 'gps_accuracy_m': gpsAccuracyM,
      if (zone != null) 'zone': zone,
      if (lga != null) 'lga': lga,
      if (ward != null) 'ward': ward,
      if (postcode != null) 'postcode': postcode,
      if (postcodeStatus != null) 'postcode_status': postcodeStatus,
      if (enumeratorId != null) 'enumerator_id': enumeratorId,
      if (enumerationDate != null) 'enumeration_date': enumerationDate,
      if (verificationStatus != null) 'verification_status': verificationStatus,
      if (rejectionReason != null) 'rejection_reason': rejectionReason,
      if (disputeReason != null) 'dispute_reason': disputeReason,
      if (verifiedBy != null) 'verified_by': verifiedBy,
      if (verifiedAt != null) 'verified_at': verifiedAt,
      if (boundaryFlag != null) 'boundary_flag': boundaryFlag,
      if (gpsAccuracyFlag != null) 'gps_accuracy_flag': gpsAccuracyFlag,
      if (duplicateFlag != null) 'duplicate_flag': duplicateFlag,
      if (qaFlags != null) 'qa_flags': qaFlags,
      if (serverId != null) 'server_id': serverId,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (lastModifiedAt != null) 'last_modified_at': lastModifiedAt,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  BuildingsCompanion copyWith(
      {Value<int>? id,
      Value<String>? buildingId,
      Value<String>? streetId,
      Value<String>? buildingType,
      Value<int>? numberOfFloors,
      Value<int>? numberOfUnits,
      Value<String>? buildingCondition,
      Value<String?>? streetAddress,
      Value<int>? hasSignage,
      Value<String?>? businessNames,
      Value<String?>? notes,
      Value<Uint8List>? geometryWkb,
      Value<double>? gpsAccuracyM,
      Value<String?>? zone,
      Value<String>? lga,
      Value<String?>? ward,
      Value<String?>? postcode,
      Value<String>? postcodeStatus,
      Value<String>? enumeratorId,
      Value<int>? enumerationDate,
      Value<String>? verificationStatus,
      Value<String?>? rejectionReason,
      Value<String?>? disputeReason,
      Value<String?>? verifiedBy,
      Value<int?>? verifiedAt,
      Value<int>? boundaryFlag,
      Value<int>? gpsAccuracyFlag,
      Value<int>? duplicateFlag,
      Value<String?>? qaFlags,
      Value<String?>? serverId,
      Value<String>? syncStatus,
      Value<int>? lastModifiedAt,
      Value<int>? createdAt}) {
    return BuildingsCompanion(
      id: id ?? this.id,
      buildingId: buildingId ?? this.buildingId,
      streetId: streetId ?? this.streetId,
      buildingType: buildingType ?? this.buildingType,
      numberOfFloors: numberOfFloors ?? this.numberOfFloors,
      numberOfUnits: numberOfUnits ?? this.numberOfUnits,
      buildingCondition: buildingCondition ?? this.buildingCondition,
      streetAddress: streetAddress ?? this.streetAddress,
      hasSignage: hasSignage ?? this.hasSignage,
      businessNames: businessNames ?? this.businessNames,
      notes: notes ?? this.notes,
      geometryWkb: geometryWkb ?? this.geometryWkb,
      gpsAccuracyM: gpsAccuracyM ?? this.gpsAccuracyM,
      zone: zone ?? this.zone,
      lga: lga ?? this.lga,
      ward: ward ?? this.ward,
      postcode: postcode ?? this.postcode,
      postcodeStatus: postcodeStatus ?? this.postcodeStatus,
      enumeratorId: enumeratorId ?? this.enumeratorId,
      enumerationDate: enumerationDate ?? this.enumerationDate,
      verificationStatus: verificationStatus ?? this.verificationStatus,
      rejectionReason: rejectionReason ?? this.rejectionReason,
      disputeReason: disputeReason ?? this.disputeReason,
      verifiedBy: verifiedBy ?? this.verifiedBy,
      verifiedAt: verifiedAt ?? this.verifiedAt,
      boundaryFlag: boundaryFlag ?? this.boundaryFlag,
      gpsAccuracyFlag: gpsAccuracyFlag ?? this.gpsAccuracyFlag,
      duplicateFlag: duplicateFlag ?? this.duplicateFlag,
      qaFlags: qaFlags ?? this.qaFlags,
      serverId: serverId ?? this.serverId,
      syncStatus: syncStatus ?? this.syncStatus,
      lastModifiedAt: lastModifiedAt ?? this.lastModifiedAt,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (buildingId.present) {
      map['building_id'] = Variable<String>(buildingId.value);
    }
    if (streetId.present) {
      map['street_id'] = Variable<String>(streetId.value);
    }
    if (buildingType.present) {
      map['building_type'] = Variable<String>(buildingType.value);
    }
    if (numberOfFloors.present) {
      map['number_of_floors'] = Variable<int>(numberOfFloors.value);
    }
    if (numberOfUnits.present) {
      map['number_of_units'] = Variable<int>(numberOfUnits.value);
    }
    if (buildingCondition.present) {
      map['building_condition'] = Variable<String>(buildingCondition.value);
    }
    if (streetAddress.present) {
      map['street_address'] = Variable<String>(streetAddress.value);
    }
    if (hasSignage.present) {
      map['has_signage'] = Variable<int>(hasSignage.value);
    }
    if (businessNames.present) {
      map['business_names'] = Variable<String>(businessNames.value);
    }
    if (notes.present) {
      map['notes'] = Variable<String>(notes.value);
    }
    if (geometryWkb.present) {
      map['geometry_wkb'] = Variable<Uint8List>(geometryWkb.value);
    }
    if (gpsAccuracyM.present) {
      map['gps_accuracy_m'] = Variable<double>(gpsAccuracyM.value);
    }
    if (zone.present) {
      map['zone'] = Variable<String>(zone.value);
    }
    if (lga.present) {
      map['lga'] = Variable<String>(lga.value);
    }
    if (ward.present) {
      map['ward'] = Variable<String>(ward.value);
    }
    if (postcode.present) {
      map['postcode'] = Variable<String>(postcode.value);
    }
    if (postcodeStatus.present) {
      map['postcode_status'] = Variable<String>(postcodeStatus.value);
    }
    if (enumeratorId.present) {
      map['enumerator_id'] = Variable<String>(enumeratorId.value);
    }
    if (enumerationDate.present) {
      map['enumeration_date'] = Variable<int>(enumerationDate.value);
    }
    if (verificationStatus.present) {
      map['verification_status'] = Variable<String>(verificationStatus.value);
    }
    if (rejectionReason.present) {
      map['rejection_reason'] = Variable<String>(rejectionReason.value);
    }
    if (disputeReason.present) {
      map['dispute_reason'] = Variable<String>(disputeReason.value);
    }
    if (verifiedBy.present) {
      map['verified_by'] = Variable<String>(verifiedBy.value);
    }
    if (verifiedAt.present) {
      map['verified_at'] = Variable<int>(verifiedAt.value);
    }
    if (boundaryFlag.present) {
      map['boundary_flag'] = Variable<int>(boundaryFlag.value);
    }
    if (gpsAccuracyFlag.present) {
      map['gps_accuracy_flag'] = Variable<int>(gpsAccuracyFlag.value);
    }
    if (duplicateFlag.present) {
      map['duplicate_flag'] = Variable<int>(duplicateFlag.value);
    }
    if (qaFlags.present) {
      map['qa_flags'] = Variable<String>(qaFlags.value);
    }
    if (serverId.present) {
      map['server_id'] = Variable<String>(serverId.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (lastModifiedAt.present) {
      map['last_modified_at'] = Variable<int>(lastModifiedAt.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<int>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('BuildingsCompanion(')
          ..write('id: $id, ')
          ..write('buildingId: $buildingId, ')
          ..write('streetId: $streetId, ')
          ..write('buildingType: $buildingType, ')
          ..write('numberOfFloors: $numberOfFloors, ')
          ..write('numberOfUnits: $numberOfUnits, ')
          ..write('buildingCondition: $buildingCondition, ')
          ..write('streetAddress: $streetAddress, ')
          ..write('hasSignage: $hasSignage, ')
          ..write('businessNames: $businessNames, ')
          ..write('notes: $notes, ')
          ..write('geometryWkb: $geometryWkb, ')
          ..write('gpsAccuracyM: $gpsAccuracyM, ')
          ..write('zone: $zone, ')
          ..write('lga: $lga, ')
          ..write('ward: $ward, ')
          ..write('postcode: $postcode, ')
          ..write('postcodeStatus: $postcodeStatus, ')
          ..write('enumeratorId: $enumeratorId, ')
          ..write('enumerationDate: $enumerationDate, ')
          ..write('verificationStatus: $verificationStatus, ')
          ..write('rejectionReason: $rejectionReason, ')
          ..write('disputeReason: $disputeReason, ')
          ..write('verifiedBy: $verifiedBy, ')
          ..write('verifiedAt: $verifiedAt, ')
          ..write('boundaryFlag: $boundaryFlag, ')
          ..write('gpsAccuracyFlag: $gpsAccuracyFlag, ')
          ..write('duplicateFlag: $duplicateFlag, ')
          ..write('qaFlags: $qaFlags, ')
          ..write('serverId: $serverId, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('lastModifiedAt: $lastModifiedAt, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

class $PhotosTable extends Photos with TableInfo<$PhotosTable, Photo> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PhotosTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _photoIdMeta =
      const VerificationMeta('photoId');
  @override
  late final GeneratedColumn<String> photoId = GeneratedColumn<String>(
      'photo_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways('UNIQUE'));
  static const VerificationMeta _recordTypeMeta =
      const VerificationMeta('recordType');
  @override
  late final GeneratedColumn<String> recordType = GeneratedColumn<String>(
      'record_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _recordLocalIdMeta =
      const VerificationMeta('recordLocalId');
  @override
  late final GeneratedColumn<int> recordLocalId = GeneratedColumn<int>(
      'record_local_id', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _filePathMeta =
      const VerificationMeta('filePath');
  @override
  late final GeneratedColumn<String> filePath = GeneratedColumn<String>(
      'file_path', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _isFrontageMeta =
      const VerificationMeta('isFrontage');
  @override
  late final GeneratedColumn<int> isFrontage = GeneratedColumn<int>(
      'is_frontage', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _latitudeMeta =
      const VerificationMeta('latitude');
  @override
  late final GeneratedColumn<double> latitude = GeneratedColumn<double>(
      'latitude', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _longitudeMeta =
      const VerificationMeta('longitude');
  @override
  late final GeneratedColumn<double> longitude = GeneratedColumn<double>(
      'longitude', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _capturedAtMeta =
      const VerificationMeta('capturedAt');
  @override
  late final GeneratedColumn<int> capturedAt = GeneratedColumn<int>(
      'captured_at', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _fileSizeBytesMeta =
      const VerificationMeta('fileSizeBytes');
  @override
  late final GeneratedColumn<int> fileSizeBytes = GeneratedColumn<int>(
      'file_size_bytes', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _brokenRefFlagMeta =
      const VerificationMeta('brokenRefFlag');
  @override
  late final GeneratedColumn<int> brokenRefFlag = GeneratedColumn<int>(
      'broken_ref_flag', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _syncStatusMeta =
      const VerificationMeta('syncStatus');
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
      'sync_status', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('queued'));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<int> createdAt = GeneratedColumn<int>(
      'created_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  @override
  List<GeneratedColumn> get $columns => [
        id,
        photoId,
        recordType,
        recordLocalId,
        filePath,
        isFrontage,
        latitude,
        longitude,
        capturedAt,
        fileSizeBytes,
        brokenRefFlag,
        syncStatus,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'photos';
  @override
  VerificationContext validateIntegrity(Insertable<Photo> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('photo_id')) {
      context.handle(_photoIdMeta,
          photoId.isAcceptableOrUnknown(data['photo_id']!, _photoIdMeta));
    } else if (isInserting) {
      context.missing(_photoIdMeta);
    }
    if (data.containsKey('record_type')) {
      context.handle(
          _recordTypeMeta,
          recordType.isAcceptableOrUnknown(
              data['record_type']!, _recordTypeMeta));
    } else if (isInserting) {
      context.missing(_recordTypeMeta);
    }
    if (data.containsKey('record_local_id')) {
      context.handle(
          _recordLocalIdMeta,
          recordLocalId.isAcceptableOrUnknown(
              data['record_local_id']!, _recordLocalIdMeta));
    } else if (isInserting) {
      context.missing(_recordLocalIdMeta);
    }
    if (data.containsKey('file_path')) {
      context.handle(_filePathMeta,
          filePath.isAcceptableOrUnknown(data['file_path']!, _filePathMeta));
    } else if (isInserting) {
      context.missing(_filePathMeta);
    }
    if (data.containsKey('is_frontage')) {
      context.handle(
          _isFrontageMeta,
          isFrontage.isAcceptableOrUnknown(
              data['is_frontage']!, _isFrontageMeta));
    }
    if (data.containsKey('latitude')) {
      context.handle(_latitudeMeta,
          latitude.isAcceptableOrUnknown(data['latitude']!, _latitudeMeta));
    } else if (isInserting) {
      context.missing(_latitudeMeta);
    }
    if (data.containsKey('longitude')) {
      context.handle(_longitudeMeta,
          longitude.isAcceptableOrUnknown(data['longitude']!, _longitudeMeta));
    } else if (isInserting) {
      context.missing(_longitudeMeta);
    }
    if (data.containsKey('captured_at')) {
      context.handle(
          _capturedAtMeta,
          capturedAt.isAcceptableOrUnknown(
              data['captured_at']!, _capturedAtMeta));
    } else if (isInserting) {
      context.missing(_capturedAtMeta);
    }
    if (data.containsKey('file_size_bytes')) {
      context.handle(
          _fileSizeBytesMeta,
          fileSizeBytes.isAcceptableOrUnknown(
              data['file_size_bytes']!, _fileSizeBytesMeta));
    }
    if (data.containsKey('broken_ref_flag')) {
      context.handle(
          _brokenRefFlagMeta,
          brokenRefFlag.isAcceptableOrUnknown(
              data['broken_ref_flag']!, _brokenRefFlagMeta));
    }
    if (data.containsKey('sync_status')) {
      context.handle(
          _syncStatusMeta,
          syncStatus.isAcceptableOrUnknown(
              data['sync_status']!, _syncStatusMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Photo map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Photo(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      photoId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}photo_id'])!,
      recordType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}record_type'])!,
      recordLocalId: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}record_local_id'])!,
      filePath: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}file_path'])!,
      isFrontage: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}is_frontage'])!,
      latitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}latitude'])!,
      longitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}longitude'])!,
      capturedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}captured_at'])!,
      fileSizeBytes: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}file_size_bytes']),
      brokenRefFlag: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}broken_ref_flag'])!,
      syncStatus: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}sync_status'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $PhotosTable createAlias(String alias) {
    return $PhotosTable(attachedDatabase, alias);
  }
}

class Photo extends DataClass implements Insertable<Photo> {
  final int id;
  final String photoId;
  final String recordType;
  final int recordLocalId;
  final String filePath;
  final int isFrontage;
  final double latitude;
  final double longitude;
  final int capturedAt;
  final int? fileSizeBytes;
  final int brokenRefFlag;
  final String syncStatus;
  final int createdAt;
  const Photo(
      {required this.id,
      required this.photoId,
      required this.recordType,
      required this.recordLocalId,
      required this.filePath,
      required this.isFrontage,
      required this.latitude,
      required this.longitude,
      required this.capturedAt,
      this.fileSizeBytes,
      required this.brokenRefFlag,
      required this.syncStatus,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['photo_id'] = Variable<String>(photoId);
    map['record_type'] = Variable<String>(recordType);
    map['record_local_id'] = Variable<int>(recordLocalId);
    map['file_path'] = Variable<String>(filePath);
    map['is_frontage'] = Variable<int>(isFrontage);
    map['latitude'] = Variable<double>(latitude);
    map['longitude'] = Variable<double>(longitude);
    map['captured_at'] = Variable<int>(capturedAt);
    if (!nullToAbsent || fileSizeBytes != null) {
      map['file_size_bytes'] = Variable<int>(fileSizeBytes);
    }
    map['broken_ref_flag'] = Variable<int>(brokenRefFlag);
    map['sync_status'] = Variable<String>(syncStatus);
    map['created_at'] = Variable<int>(createdAt);
    return map;
  }

  PhotosCompanion toCompanion(bool nullToAbsent) {
    return PhotosCompanion(
      id: Value(id),
      photoId: Value(photoId),
      recordType: Value(recordType),
      recordLocalId: Value(recordLocalId),
      filePath: Value(filePath),
      isFrontage: Value(isFrontage),
      latitude: Value(latitude),
      longitude: Value(longitude),
      capturedAt: Value(capturedAt),
      fileSizeBytes: fileSizeBytes == null && nullToAbsent
          ? const Value.absent()
          : Value(fileSizeBytes),
      brokenRefFlag: Value(brokenRefFlag),
      syncStatus: Value(syncStatus),
      createdAt: Value(createdAt),
    );
  }

  factory Photo.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Photo(
      id: serializer.fromJson<int>(json['id']),
      photoId: serializer.fromJson<String>(json['photoId']),
      recordType: serializer.fromJson<String>(json['recordType']),
      recordLocalId: serializer.fromJson<int>(json['recordLocalId']),
      filePath: serializer.fromJson<String>(json['filePath']),
      isFrontage: serializer.fromJson<int>(json['isFrontage']),
      latitude: serializer.fromJson<double>(json['latitude']),
      longitude: serializer.fromJson<double>(json['longitude']),
      capturedAt: serializer.fromJson<int>(json['capturedAt']),
      fileSizeBytes: serializer.fromJson<int?>(json['fileSizeBytes']),
      brokenRefFlag: serializer.fromJson<int>(json['brokenRefFlag']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      createdAt: serializer.fromJson<int>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'photoId': serializer.toJson<String>(photoId),
      'recordType': serializer.toJson<String>(recordType),
      'recordLocalId': serializer.toJson<int>(recordLocalId),
      'filePath': serializer.toJson<String>(filePath),
      'isFrontage': serializer.toJson<int>(isFrontage),
      'latitude': serializer.toJson<double>(latitude),
      'longitude': serializer.toJson<double>(longitude),
      'capturedAt': serializer.toJson<int>(capturedAt),
      'fileSizeBytes': serializer.toJson<int?>(fileSizeBytes),
      'brokenRefFlag': serializer.toJson<int>(brokenRefFlag),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'createdAt': serializer.toJson<int>(createdAt),
    };
  }

  Photo copyWith(
          {int? id,
          String? photoId,
          String? recordType,
          int? recordLocalId,
          String? filePath,
          int? isFrontage,
          double? latitude,
          double? longitude,
          int? capturedAt,
          Value<int?> fileSizeBytes = const Value.absent(),
          int? brokenRefFlag,
          String? syncStatus,
          int? createdAt}) =>
      Photo(
        id: id ?? this.id,
        photoId: photoId ?? this.photoId,
        recordType: recordType ?? this.recordType,
        recordLocalId: recordLocalId ?? this.recordLocalId,
        filePath: filePath ?? this.filePath,
        isFrontage: isFrontage ?? this.isFrontage,
        latitude: latitude ?? this.latitude,
        longitude: longitude ?? this.longitude,
        capturedAt: capturedAt ?? this.capturedAt,
        fileSizeBytes:
            fileSizeBytes.present ? fileSizeBytes.value : this.fileSizeBytes,
        brokenRefFlag: brokenRefFlag ?? this.brokenRefFlag,
        syncStatus: syncStatus ?? this.syncStatus,
        createdAt: createdAt ?? this.createdAt,
      );
  Photo copyWithCompanion(PhotosCompanion data) {
    return Photo(
      id: data.id.present ? data.id.value : this.id,
      photoId: data.photoId.present ? data.photoId.value : this.photoId,
      recordType:
          data.recordType.present ? data.recordType.value : this.recordType,
      recordLocalId: data.recordLocalId.present
          ? data.recordLocalId.value
          : this.recordLocalId,
      filePath: data.filePath.present ? data.filePath.value : this.filePath,
      isFrontage:
          data.isFrontage.present ? data.isFrontage.value : this.isFrontage,
      latitude: data.latitude.present ? data.latitude.value : this.latitude,
      longitude: data.longitude.present ? data.longitude.value : this.longitude,
      capturedAt:
          data.capturedAt.present ? data.capturedAt.value : this.capturedAt,
      fileSizeBytes: data.fileSizeBytes.present
          ? data.fileSizeBytes.value
          : this.fileSizeBytes,
      brokenRefFlag: data.brokenRefFlag.present
          ? data.brokenRefFlag.value
          : this.brokenRefFlag,
      syncStatus:
          data.syncStatus.present ? data.syncStatus.value : this.syncStatus,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Photo(')
          ..write('id: $id, ')
          ..write('photoId: $photoId, ')
          ..write('recordType: $recordType, ')
          ..write('recordLocalId: $recordLocalId, ')
          ..write('filePath: $filePath, ')
          ..write('isFrontage: $isFrontage, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('capturedAt: $capturedAt, ')
          ..write('fileSizeBytes: $fileSizeBytes, ')
          ..write('brokenRefFlag: $brokenRefFlag, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      photoId,
      recordType,
      recordLocalId,
      filePath,
      isFrontage,
      latitude,
      longitude,
      capturedAt,
      fileSizeBytes,
      brokenRefFlag,
      syncStatus,
      createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Photo &&
          other.id == this.id &&
          other.photoId == this.photoId &&
          other.recordType == this.recordType &&
          other.recordLocalId == this.recordLocalId &&
          other.filePath == this.filePath &&
          other.isFrontage == this.isFrontage &&
          other.latitude == this.latitude &&
          other.longitude == this.longitude &&
          other.capturedAt == this.capturedAt &&
          other.fileSizeBytes == this.fileSizeBytes &&
          other.brokenRefFlag == this.brokenRefFlag &&
          other.syncStatus == this.syncStatus &&
          other.createdAt == this.createdAt);
}

class PhotosCompanion extends UpdateCompanion<Photo> {
  final Value<int> id;
  final Value<String> photoId;
  final Value<String> recordType;
  final Value<int> recordLocalId;
  final Value<String> filePath;
  final Value<int> isFrontage;
  final Value<double> latitude;
  final Value<double> longitude;
  final Value<int> capturedAt;
  final Value<int?> fileSizeBytes;
  final Value<int> brokenRefFlag;
  final Value<String> syncStatus;
  final Value<int> createdAt;
  const PhotosCompanion({
    this.id = const Value.absent(),
    this.photoId = const Value.absent(),
    this.recordType = const Value.absent(),
    this.recordLocalId = const Value.absent(),
    this.filePath = const Value.absent(),
    this.isFrontage = const Value.absent(),
    this.latitude = const Value.absent(),
    this.longitude = const Value.absent(),
    this.capturedAt = const Value.absent(),
    this.fileSizeBytes = const Value.absent(),
    this.brokenRefFlag = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  PhotosCompanion.insert({
    this.id = const Value.absent(),
    required String photoId,
    required String recordType,
    required int recordLocalId,
    required String filePath,
    this.isFrontage = const Value.absent(),
    required double latitude,
    required double longitude,
    required int capturedAt,
    this.fileSizeBytes = const Value.absent(),
    this.brokenRefFlag = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : photoId = Value(photoId),
        recordType = Value(recordType),
        recordLocalId = Value(recordLocalId),
        filePath = Value(filePath),
        latitude = Value(latitude),
        longitude = Value(longitude),
        capturedAt = Value(capturedAt);
  static Insertable<Photo> custom({
    Expression<int>? id,
    Expression<String>? photoId,
    Expression<String>? recordType,
    Expression<int>? recordLocalId,
    Expression<String>? filePath,
    Expression<int>? isFrontage,
    Expression<double>? latitude,
    Expression<double>? longitude,
    Expression<int>? capturedAt,
    Expression<int>? fileSizeBytes,
    Expression<int>? brokenRefFlag,
    Expression<String>? syncStatus,
    Expression<int>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (photoId != null) 'photo_id': photoId,
      if (recordType != null) 'record_type': recordType,
      if (recordLocalId != null) 'record_local_id': recordLocalId,
      if (filePath != null) 'file_path': filePath,
      if (isFrontage != null) 'is_frontage': isFrontage,
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
      if (capturedAt != null) 'captured_at': capturedAt,
      if (fileSizeBytes != null) 'file_size_bytes': fileSizeBytes,
      if (brokenRefFlag != null) 'broken_ref_flag': brokenRefFlag,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  PhotosCompanion copyWith(
      {Value<int>? id,
      Value<String>? photoId,
      Value<String>? recordType,
      Value<int>? recordLocalId,
      Value<String>? filePath,
      Value<int>? isFrontage,
      Value<double>? latitude,
      Value<double>? longitude,
      Value<int>? capturedAt,
      Value<int?>? fileSizeBytes,
      Value<int>? brokenRefFlag,
      Value<String>? syncStatus,
      Value<int>? createdAt}) {
    return PhotosCompanion(
      id: id ?? this.id,
      photoId: photoId ?? this.photoId,
      recordType: recordType ?? this.recordType,
      recordLocalId: recordLocalId ?? this.recordLocalId,
      filePath: filePath ?? this.filePath,
      isFrontage: isFrontage ?? this.isFrontage,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      capturedAt: capturedAt ?? this.capturedAt,
      fileSizeBytes: fileSizeBytes ?? this.fileSizeBytes,
      brokenRefFlag: brokenRefFlag ?? this.brokenRefFlag,
      syncStatus: syncStatus ?? this.syncStatus,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (photoId.present) {
      map['photo_id'] = Variable<String>(photoId.value);
    }
    if (recordType.present) {
      map['record_type'] = Variable<String>(recordType.value);
    }
    if (recordLocalId.present) {
      map['record_local_id'] = Variable<int>(recordLocalId.value);
    }
    if (filePath.present) {
      map['file_path'] = Variable<String>(filePath.value);
    }
    if (isFrontage.present) {
      map['is_frontage'] = Variable<int>(isFrontage.value);
    }
    if (latitude.present) {
      map['latitude'] = Variable<double>(latitude.value);
    }
    if (longitude.present) {
      map['longitude'] = Variable<double>(longitude.value);
    }
    if (capturedAt.present) {
      map['captured_at'] = Variable<int>(capturedAt.value);
    }
    if (fileSizeBytes.present) {
      map['file_size_bytes'] = Variable<int>(fileSizeBytes.value);
    }
    if (brokenRefFlag.present) {
      map['broken_ref_flag'] = Variable<int>(brokenRefFlag.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<int>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PhotosCompanion(')
          ..write('id: $id, ')
          ..write('photoId: $photoId, ')
          ..write('recordType: $recordType, ')
          ..write('recordLocalId: $recordLocalId, ')
          ..write('filePath: $filePath, ')
          ..write('isFrontage: $isFrontage, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('capturedAt: $capturedAt, ')
          ..write('fileSizeBytes: $fileSizeBytes, ')
          ..write('brokenRefFlag: $brokenRefFlag, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

class $SyncQueueTable extends SyncQueue
    with TableInfo<$SyncQueueTable, SyncQueueData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncQueueTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _operationMeta =
      const VerificationMeta('operation');
  @override
  late final GeneratedColumn<String> operation = GeneratedColumn<String>(
      'operation', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _entityTypeMeta =
      const VerificationMeta('entityType');
  @override
  late final GeneratedColumn<String> entityType = GeneratedColumn<String>(
      'entity_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _entityLocalIdMeta =
      const VerificationMeta('entityLocalId');
  @override
  late final GeneratedColumn<int> entityLocalId = GeneratedColumn<int>(
      'entity_local_id', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _payloadJsonMeta =
      const VerificationMeta('payloadJson');
  @override
  late final GeneratedColumn<String> payloadJson = GeneratedColumn<String>(
      'payload_json', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _attemptCountMeta =
      const VerificationMeta('attemptCount');
  @override
  late final GeneratedColumn<int> attemptCount = GeneratedColumn<int>(
      'attempt_count', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _lastAttemptAtMeta =
      const VerificationMeta('lastAttemptAt');
  @override
  late final GeneratedColumn<int> lastAttemptAt = GeneratedColumn<int>(
      'last_attempt_at', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _lastErrorMeta =
      const VerificationMeta('lastError');
  @override
  late final GeneratedColumn<String> lastError = GeneratedColumn<String>(
      'last_error', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
      'status', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('pending'));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<int> createdAt = GeneratedColumn<int>(
      'created_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  @override
  List<GeneratedColumn> get $columns => [
        id,
        operation,
        entityType,
        entityLocalId,
        payloadJson,
        attemptCount,
        lastAttemptAt,
        lastError,
        status,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_queue';
  @override
  VerificationContext validateIntegrity(Insertable<SyncQueueData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('operation')) {
      context.handle(_operationMeta,
          operation.isAcceptableOrUnknown(data['operation']!, _operationMeta));
    } else if (isInserting) {
      context.missing(_operationMeta);
    }
    if (data.containsKey('entity_type')) {
      context.handle(
          _entityTypeMeta,
          entityType.isAcceptableOrUnknown(
              data['entity_type']!, _entityTypeMeta));
    } else if (isInserting) {
      context.missing(_entityTypeMeta);
    }
    if (data.containsKey('entity_local_id')) {
      context.handle(
          _entityLocalIdMeta,
          entityLocalId.isAcceptableOrUnknown(
              data['entity_local_id']!, _entityLocalIdMeta));
    } else if (isInserting) {
      context.missing(_entityLocalIdMeta);
    }
    if (data.containsKey('payload_json')) {
      context.handle(
          _payloadJsonMeta,
          payloadJson.isAcceptableOrUnknown(
              data['payload_json']!, _payloadJsonMeta));
    } else if (isInserting) {
      context.missing(_payloadJsonMeta);
    }
    if (data.containsKey('attempt_count')) {
      context.handle(
          _attemptCountMeta,
          attemptCount.isAcceptableOrUnknown(
              data['attempt_count']!, _attemptCountMeta));
    }
    if (data.containsKey('last_attempt_at')) {
      context.handle(
          _lastAttemptAtMeta,
          lastAttemptAt.isAcceptableOrUnknown(
              data['last_attempt_at']!, _lastAttemptAtMeta));
    }
    if (data.containsKey('last_error')) {
      context.handle(_lastErrorMeta,
          lastError.isAcceptableOrUnknown(data['last_error']!, _lastErrorMeta));
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta,
          status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  SyncQueueData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncQueueData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      operation: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}operation'])!,
      entityType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}entity_type'])!,
      entityLocalId: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}entity_local_id'])!,
      payloadJson: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}payload_json'])!,
      attemptCount: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}attempt_count'])!,
      lastAttemptAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}last_attempt_at']),
      lastError: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}last_error']),
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}status'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $SyncQueueTable createAlias(String alias) {
    return $SyncQueueTable(attachedDatabase, alias);
  }
}

class SyncQueueData extends DataClass implements Insertable<SyncQueueData> {
  final int id;
  final String operation;
  final String entityType;
  final int entityLocalId;
  final String payloadJson;
  final int attemptCount;
  final int? lastAttemptAt;
  final String? lastError;
  final String status;
  final int createdAt;
  const SyncQueueData(
      {required this.id,
      required this.operation,
      required this.entityType,
      required this.entityLocalId,
      required this.payloadJson,
      required this.attemptCount,
      this.lastAttemptAt,
      this.lastError,
      required this.status,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['operation'] = Variable<String>(operation);
    map['entity_type'] = Variable<String>(entityType);
    map['entity_local_id'] = Variable<int>(entityLocalId);
    map['payload_json'] = Variable<String>(payloadJson);
    map['attempt_count'] = Variable<int>(attemptCount);
    if (!nullToAbsent || lastAttemptAt != null) {
      map['last_attempt_at'] = Variable<int>(lastAttemptAt);
    }
    if (!nullToAbsent || lastError != null) {
      map['last_error'] = Variable<String>(lastError);
    }
    map['status'] = Variable<String>(status);
    map['created_at'] = Variable<int>(createdAt);
    return map;
  }

  SyncQueueCompanion toCompanion(bool nullToAbsent) {
    return SyncQueueCompanion(
      id: Value(id),
      operation: Value(operation),
      entityType: Value(entityType),
      entityLocalId: Value(entityLocalId),
      payloadJson: Value(payloadJson),
      attemptCount: Value(attemptCount),
      lastAttemptAt: lastAttemptAt == null && nullToAbsent
          ? const Value.absent()
          : Value(lastAttemptAt),
      lastError: lastError == null && nullToAbsent
          ? const Value.absent()
          : Value(lastError),
      status: Value(status),
      createdAt: Value(createdAt),
    );
  }

  factory SyncQueueData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncQueueData(
      id: serializer.fromJson<int>(json['id']),
      operation: serializer.fromJson<String>(json['operation']),
      entityType: serializer.fromJson<String>(json['entityType']),
      entityLocalId: serializer.fromJson<int>(json['entityLocalId']),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      attemptCount: serializer.fromJson<int>(json['attemptCount']),
      lastAttemptAt: serializer.fromJson<int?>(json['lastAttemptAt']),
      lastError: serializer.fromJson<String?>(json['lastError']),
      status: serializer.fromJson<String>(json['status']),
      createdAt: serializer.fromJson<int>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'operation': serializer.toJson<String>(operation),
      'entityType': serializer.toJson<String>(entityType),
      'entityLocalId': serializer.toJson<int>(entityLocalId),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'attemptCount': serializer.toJson<int>(attemptCount),
      'lastAttemptAt': serializer.toJson<int?>(lastAttemptAt),
      'lastError': serializer.toJson<String?>(lastError),
      'status': serializer.toJson<String>(status),
      'createdAt': serializer.toJson<int>(createdAt),
    };
  }

  SyncQueueData copyWith(
          {int? id,
          String? operation,
          String? entityType,
          int? entityLocalId,
          String? payloadJson,
          int? attemptCount,
          Value<int?> lastAttemptAt = const Value.absent(),
          Value<String?> lastError = const Value.absent(),
          String? status,
          int? createdAt}) =>
      SyncQueueData(
        id: id ?? this.id,
        operation: operation ?? this.operation,
        entityType: entityType ?? this.entityType,
        entityLocalId: entityLocalId ?? this.entityLocalId,
        payloadJson: payloadJson ?? this.payloadJson,
        attemptCount: attemptCount ?? this.attemptCount,
        lastAttemptAt:
            lastAttemptAt.present ? lastAttemptAt.value : this.lastAttemptAt,
        lastError: lastError.present ? lastError.value : this.lastError,
        status: status ?? this.status,
        createdAt: createdAt ?? this.createdAt,
      );
  SyncQueueData copyWithCompanion(SyncQueueCompanion data) {
    return SyncQueueData(
      id: data.id.present ? data.id.value : this.id,
      operation: data.operation.present ? data.operation.value : this.operation,
      entityType:
          data.entityType.present ? data.entityType.value : this.entityType,
      entityLocalId: data.entityLocalId.present
          ? data.entityLocalId.value
          : this.entityLocalId,
      payloadJson:
          data.payloadJson.present ? data.payloadJson.value : this.payloadJson,
      attemptCount: data.attemptCount.present
          ? data.attemptCount.value
          : this.attemptCount,
      lastAttemptAt: data.lastAttemptAt.present
          ? data.lastAttemptAt.value
          : this.lastAttemptAt,
      lastError: data.lastError.present ? data.lastError.value : this.lastError,
      status: data.status.present ? data.status.value : this.status,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueData(')
          ..write('id: $id, ')
          ..write('operation: $operation, ')
          ..write('entityType: $entityType, ')
          ..write('entityLocalId: $entityLocalId, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('attemptCount: $attemptCount, ')
          ..write('lastAttemptAt: $lastAttemptAt, ')
          ..write('lastError: $lastError, ')
          ..write('status: $status, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, operation, entityType, entityLocalId,
      payloadJson, attemptCount, lastAttemptAt, lastError, status, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncQueueData &&
          other.id == this.id &&
          other.operation == this.operation &&
          other.entityType == this.entityType &&
          other.entityLocalId == this.entityLocalId &&
          other.payloadJson == this.payloadJson &&
          other.attemptCount == this.attemptCount &&
          other.lastAttemptAt == this.lastAttemptAt &&
          other.lastError == this.lastError &&
          other.status == this.status &&
          other.createdAt == this.createdAt);
}

class SyncQueueCompanion extends UpdateCompanion<SyncQueueData> {
  final Value<int> id;
  final Value<String> operation;
  final Value<String> entityType;
  final Value<int> entityLocalId;
  final Value<String> payloadJson;
  final Value<int> attemptCount;
  final Value<int?> lastAttemptAt;
  final Value<String?> lastError;
  final Value<String> status;
  final Value<int> createdAt;
  const SyncQueueCompanion({
    this.id = const Value.absent(),
    this.operation = const Value.absent(),
    this.entityType = const Value.absent(),
    this.entityLocalId = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.attemptCount = const Value.absent(),
    this.lastAttemptAt = const Value.absent(),
    this.lastError = const Value.absent(),
    this.status = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  SyncQueueCompanion.insert({
    this.id = const Value.absent(),
    required String operation,
    required String entityType,
    required int entityLocalId,
    required String payloadJson,
    this.attemptCount = const Value.absent(),
    this.lastAttemptAt = const Value.absent(),
    this.lastError = const Value.absent(),
    this.status = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : operation = Value(operation),
        entityType = Value(entityType),
        entityLocalId = Value(entityLocalId),
        payloadJson = Value(payloadJson);
  static Insertable<SyncQueueData> custom({
    Expression<int>? id,
    Expression<String>? operation,
    Expression<String>? entityType,
    Expression<int>? entityLocalId,
    Expression<String>? payloadJson,
    Expression<int>? attemptCount,
    Expression<int>? lastAttemptAt,
    Expression<String>? lastError,
    Expression<String>? status,
    Expression<int>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (operation != null) 'operation': operation,
      if (entityType != null) 'entity_type': entityType,
      if (entityLocalId != null) 'entity_local_id': entityLocalId,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (attemptCount != null) 'attempt_count': attemptCount,
      if (lastAttemptAt != null) 'last_attempt_at': lastAttemptAt,
      if (lastError != null) 'last_error': lastError,
      if (status != null) 'status': status,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  SyncQueueCompanion copyWith(
      {Value<int>? id,
      Value<String>? operation,
      Value<String>? entityType,
      Value<int>? entityLocalId,
      Value<String>? payloadJson,
      Value<int>? attemptCount,
      Value<int?>? lastAttemptAt,
      Value<String?>? lastError,
      Value<String>? status,
      Value<int>? createdAt}) {
    return SyncQueueCompanion(
      id: id ?? this.id,
      operation: operation ?? this.operation,
      entityType: entityType ?? this.entityType,
      entityLocalId: entityLocalId ?? this.entityLocalId,
      payloadJson: payloadJson ?? this.payloadJson,
      attemptCount: attemptCount ?? this.attemptCount,
      lastAttemptAt: lastAttemptAt ?? this.lastAttemptAt,
      lastError: lastError ?? this.lastError,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (operation.present) {
      map['operation'] = Variable<String>(operation.value);
    }
    if (entityType.present) {
      map['entity_type'] = Variable<String>(entityType.value);
    }
    if (entityLocalId.present) {
      map['entity_local_id'] = Variable<int>(entityLocalId.value);
    }
    if (payloadJson.present) {
      map['payload_json'] = Variable<String>(payloadJson.value);
    }
    if (attemptCount.present) {
      map['attempt_count'] = Variable<int>(attemptCount.value);
    }
    if (lastAttemptAt.present) {
      map['last_attempt_at'] = Variable<int>(lastAttemptAt.value);
    }
    if (lastError.present) {
      map['last_error'] = Variable<String>(lastError.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<int>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueCompanion(')
          ..write('id: $id, ')
          ..write('operation: $operation, ')
          ..write('entityType: $entityType, ')
          ..write('entityLocalId: $entityLocalId, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('attemptCount: $attemptCount, ')
          ..write('lastAttemptAt: $lastAttemptAt, ')
          ..write('lastError: $lastError, ')
          ..write('status: $status, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

class $AuditLogTable extends AuditLog
    with TableInfo<$AuditLogTable, AuditLogData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $AuditLogTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _userIdMeta = const VerificationMeta('userId');
  @override
  late final GeneratedColumn<String> userId = GeneratedColumn<String>(
      'user_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _operationMeta =
      const VerificationMeta('operation');
  @override
  late final GeneratedColumn<String> operation = GeneratedColumn<String>(
      'operation', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _entityTypeMeta =
      const VerificationMeta('entityType');
  @override
  late final GeneratedColumn<String> entityType = GeneratedColumn<String>(
      'entity_type', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _entityIdMeta =
      const VerificationMeta('entityId');
  @override
  late final GeneratedColumn<String> entityId = GeneratedColumn<String>(
      'entity_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _detailJsonMeta =
      const VerificationMeta('detailJson');
  @override
  late final GeneratedColumn<String> detailJson = GeneratedColumn<String>(
      'detail_json', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _occurredAtMeta =
      const VerificationMeta('occurredAt');
  @override
  late final GeneratedColumn<int> occurredAt = GeneratedColumn<int>(
      'occurred_at', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  @override
  List<GeneratedColumn> get $columns =>
      [id, userId, operation, entityType, entityId, detailJson, occurredAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'audit_log';
  @override
  VerificationContext validateIntegrity(Insertable<AuditLogData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('user_id')) {
      context.handle(_userIdMeta,
          userId.isAcceptableOrUnknown(data['user_id']!, _userIdMeta));
    } else if (isInserting) {
      context.missing(_userIdMeta);
    }
    if (data.containsKey('operation')) {
      context.handle(_operationMeta,
          operation.isAcceptableOrUnknown(data['operation']!, _operationMeta));
    } else if (isInserting) {
      context.missing(_operationMeta);
    }
    if (data.containsKey('entity_type')) {
      context.handle(
          _entityTypeMeta,
          entityType.isAcceptableOrUnknown(
              data['entity_type']!, _entityTypeMeta));
    }
    if (data.containsKey('entity_id')) {
      context.handle(_entityIdMeta,
          entityId.isAcceptableOrUnknown(data['entity_id']!, _entityIdMeta));
    }
    if (data.containsKey('detail_json')) {
      context.handle(
          _detailJsonMeta,
          detailJson.isAcceptableOrUnknown(
              data['detail_json']!, _detailJsonMeta));
    }
    if (data.containsKey('occurred_at')) {
      context.handle(
          _occurredAtMeta,
          occurredAt.isAcceptableOrUnknown(
              data['occurred_at']!, _occurredAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  AuditLogData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return AuditLogData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      userId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}user_id'])!,
      operation: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}operation'])!,
      entityType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}entity_type']),
      entityId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}entity_id']),
      detailJson: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}detail_json']),
      occurredAt: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}occurred_at'])!,
    );
  }

  @override
  $AuditLogTable createAlias(String alias) {
    return $AuditLogTable(attachedDatabase, alias);
  }
}

class AuditLogData extends DataClass implements Insertable<AuditLogData> {
  final int id;
  final String userId;
  final String operation;
  final String? entityType;
  final String? entityId;
  final String? detailJson;
  final int occurredAt;
  const AuditLogData(
      {required this.id,
      required this.userId,
      required this.operation,
      this.entityType,
      this.entityId,
      this.detailJson,
      required this.occurredAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['user_id'] = Variable<String>(userId);
    map['operation'] = Variable<String>(operation);
    if (!nullToAbsent || entityType != null) {
      map['entity_type'] = Variable<String>(entityType);
    }
    if (!nullToAbsent || entityId != null) {
      map['entity_id'] = Variable<String>(entityId);
    }
    if (!nullToAbsent || detailJson != null) {
      map['detail_json'] = Variable<String>(detailJson);
    }
    map['occurred_at'] = Variable<int>(occurredAt);
    return map;
  }

  AuditLogCompanion toCompanion(bool nullToAbsent) {
    return AuditLogCompanion(
      id: Value(id),
      userId: Value(userId),
      operation: Value(operation),
      entityType: entityType == null && nullToAbsent
          ? const Value.absent()
          : Value(entityType),
      entityId: entityId == null && nullToAbsent
          ? const Value.absent()
          : Value(entityId),
      detailJson: detailJson == null && nullToAbsent
          ? const Value.absent()
          : Value(detailJson),
      occurredAt: Value(occurredAt),
    );
  }

  factory AuditLogData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return AuditLogData(
      id: serializer.fromJson<int>(json['id']),
      userId: serializer.fromJson<String>(json['userId']),
      operation: serializer.fromJson<String>(json['operation']),
      entityType: serializer.fromJson<String?>(json['entityType']),
      entityId: serializer.fromJson<String?>(json['entityId']),
      detailJson: serializer.fromJson<String?>(json['detailJson']),
      occurredAt: serializer.fromJson<int>(json['occurredAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'userId': serializer.toJson<String>(userId),
      'operation': serializer.toJson<String>(operation),
      'entityType': serializer.toJson<String?>(entityType),
      'entityId': serializer.toJson<String?>(entityId),
      'detailJson': serializer.toJson<String?>(detailJson),
      'occurredAt': serializer.toJson<int>(occurredAt),
    };
  }

  AuditLogData copyWith(
          {int? id,
          String? userId,
          String? operation,
          Value<String?> entityType = const Value.absent(),
          Value<String?> entityId = const Value.absent(),
          Value<String?> detailJson = const Value.absent(),
          int? occurredAt}) =>
      AuditLogData(
        id: id ?? this.id,
        userId: userId ?? this.userId,
        operation: operation ?? this.operation,
        entityType: entityType.present ? entityType.value : this.entityType,
        entityId: entityId.present ? entityId.value : this.entityId,
        detailJson: detailJson.present ? detailJson.value : this.detailJson,
        occurredAt: occurredAt ?? this.occurredAt,
      );
  AuditLogData copyWithCompanion(AuditLogCompanion data) {
    return AuditLogData(
      id: data.id.present ? data.id.value : this.id,
      userId: data.userId.present ? data.userId.value : this.userId,
      operation: data.operation.present ? data.operation.value : this.operation,
      entityType:
          data.entityType.present ? data.entityType.value : this.entityType,
      entityId: data.entityId.present ? data.entityId.value : this.entityId,
      detailJson:
          data.detailJson.present ? data.detailJson.value : this.detailJson,
      occurredAt:
          data.occurredAt.present ? data.occurredAt.value : this.occurredAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('AuditLogData(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('operation: $operation, ')
          ..write('entityType: $entityType, ')
          ..write('entityId: $entityId, ')
          ..write('detailJson: $detailJson, ')
          ..write('occurredAt: $occurredAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id, userId, operation, entityType, entityId, detailJson, occurredAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is AuditLogData &&
          other.id == this.id &&
          other.userId == this.userId &&
          other.operation == this.operation &&
          other.entityType == this.entityType &&
          other.entityId == this.entityId &&
          other.detailJson == this.detailJson &&
          other.occurredAt == this.occurredAt);
}

class AuditLogCompanion extends UpdateCompanion<AuditLogData> {
  final Value<int> id;
  final Value<String> userId;
  final Value<String> operation;
  final Value<String?> entityType;
  final Value<String?> entityId;
  final Value<String?> detailJson;
  final Value<int> occurredAt;
  const AuditLogCompanion({
    this.id = const Value.absent(),
    this.userId = const Value.absent(),
    this.operation = const Value.absent(),
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    this.detailJson = const Value.absent(),
    this.occurredAt = const Value.absent(),
  });
  AuditLogCompanion.insert({
    this.id = const Value.absent(),
    required String userId,
    required String operation,
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    this.detailJson = const Value.absent(),
    this.occurredAt = const Value.absent(),
  })  : userId = Value(userId),
        operation = Value(operation);
  static Insertable<AuditLogData> custom({
    Expression<int>? id,
    Expression<String>? userId,
    Expression<String>? operation,
    Expression<String>? entityType,
    Expression<String>? entityId,
    Expression<String>? detailJson,
    Expression<int>? occurredAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (userId != null) 'user_id': userId,
      if (operation != null) 'operation': operation,
      if (entityType != null) 'entity_type': entityType,
      if (entityId != null) 'entity_id': entityId,
      if (detailJson != null) 'detail_json': detailJson,
      if (occurredAt != null) 'occurred_at': occurredAt,
    });
  }

  AuditLogCompanion copyWith(
      {Value<int>? id,
      Value<String>? userId,
      Value<String>? operation,
      Value<String?>? entityType,
      Value<String?>? entityId,
      Value<String?>? detailJson,
      Value<int>? occurredAt}) {
    return AuditLogCompanion(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      operation: operation ?? this.operation,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      detailJson: detailJson ?? this.detailJson,
      occurredAt: occurredAt ?? this.occurredAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (userId.present) {
      map['user_id'] = Variable<String>(userId.value);
    }
    if (operation.present) {
      map['operation'] = Variable<String>(operation.value);
    }
    if (entityType.present) {
      map['entity_type'] = Variable<String>(entityType.value);
    }
    if (entityId.present) {
      map['entity_id'] = Variable<String>(entityId.value);
    }
    if (detailJson.present) {
      map['detail_json'] = Variable<String>(detailJson.value);
    }
    if (occurredAt.present) {
      map['occurred_at'] = Variable<int>(occurredAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('AuditLogCompanion(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('operation: $operation, ')
          ..write('entityType: $entityType, ')
          ..write('entityId: $entityId, ')
          ..write('detailJson: $detailJson, ')
          ..write('occurredAt: $occurredAt')
          ..write(')'))
        .toString();
  }
}

class $DeviceSettingsTable extends DeviceSettings
    with TableInfo<$DeviceSettingsTable, DeviceSetting> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $DeviceSettingsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _keyMeta = const VerificationMeta('key');
  @override
  late final GeneratedColumn<String> key = GeneratedColumn<String>(
      'key', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways('UNIQUE'));
  static const VerificationMeta _valueMeta = const VerificationMeta('value');
  @override
  late final GeneratedColumn<String> value = GeneratedColumn<String>(
      'value', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  @override
  List<GeneratedColumn> get $columns => [id, key, value];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'device_settings';
  @override
  VerificationContext validateIntegrity(Insertable<DeviceSetting> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('key')) {
      context.handle(
          _keyMeta, key.isAcceptableOrUnknown(data['key']!, _keyMeta));
    } else if (isInserting) {
      context.missing(_keyMeta);
    }
    if (data.containsKey('value')) {
      context.handle(
          _valueMeta, value.isAcceptableOrUnknown(data['value']!, _valueMeta));
    } else if (isInserting) {
      context.missing(_valueMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  DeviceSetting map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return DeviceSetting(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      key: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}key'])!,
      value: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}value'])!,
    );
  }

  @override
  $DeviceSettingsTable createAlias(String alias) {
    return $DeviceSettingsTable(attachedDatabase, alias);
  }
}

class DeviceSetting extends DataClass implements Insertable<DeviceSetting> {
  final int id;
  final String key;
  final String value;
  const DeviceSetting(
      {required this.id, required this.key, required this.value});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['key'] = Variable<String>(key);
    map['value'] = Variable<String>(value);
    return map;
  }

  DeviceSettingsCompanion toCompanion(bool nullToAbsent) {
    return DeviceSettingsCompanion(
      id: Value(id),
      key: Value(key),
      value: Value(value),
    );
  }

  factory DeviceSetting.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return DeviceSetting(
      id: serializer.fromJson<int>(json['id']),
      key: serializer.fromJson<String>(json['key']),
      value: serializer.fromJson<String>(json['value']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'key': serializer.toJson<String>(key),
      'value': serializer.toJson<String>(value),
    };
  }

  DeviceSetting copyWith({int? id, String? key, String? value}) =>
      DeviceSetting(
        id: id ?? this.id,
        key: key ?? this.key,
        value: value ?? this.value,
      );
  DeviceSetting copyWithCompanion(DeviceSettingsCompanion data) {
    return DeviceSetting(
      id: data.id.present ? data.id.value : this.id,
      key: data.key.present ? data.key.value : this.key,
      value: data.value.present ? data.value.value : this.value,
    );
  }

  @override
  String toString() {
    return (StringBuffer('DeviceSetting(')
          ..write('id: $id, ')
          ..write('key: $key, ')
          ..write('value: $value')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, key, value);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is DeviceSetting &&
          other.id == this.id &&
          other.key == this.key &&
          other.value == this.value);
}

class DeviceSettingsCompanion extends UpdateCompanion<DeviceSetting> {
  final Value<int> id;
  final Value<String> key;
  final Value<String> value;
  const DeviceSettingsCompanion({
    this.id = const Value.absent(),
    this.key = const Value.absent(),
    this.value = const Value.absent(),
  });
  DeviceSettingsCompanion.insert({
    this.id = const Value.absent(),
    required String key,
    required String value,
  })  : key = Value(key),
        value = Value(value);
  static Insertable<DeviceSetting> custom({
    Expression<int>? id,
    Expression<String>? key,
    Expression<String>? value,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (key != null) 'key': key,
      if (value != null) 'value': value,
    });
  }

  DeviceSettingsCompanion copyWith(
      {Value<int>? id, Value<String>? key, Value<String>? value}) {
    return DeviceSettingsCompanion(
      id: id ?? this.id,
      key: key ?? this.key,
      value: value ?? this.value,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (key.present) {
      map['key'] = Variable<String>(key.value);
    }
    if (value.present) {
      map['value'] = Variable<String>(value.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('DeviceSettingsCompanion(')
          ..write('id: $id, ')
          ..write('key: $key, ')
          ..write('value: $value')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $SessionsTable sessions = $SessionsTable(this);
  late final $DropdownConfigTable dropdownConfig = $DropdownConfigTable(this);
  late final $BoundaryZonesTable boundaryZones = $BoundaryZonesTable(this);
  late final $StreetsTable streets = $StreetsTable(this);
  late final $BuildingsTable buildings = $BuildingsTable(this);
  late final $PhotosTable photos = $PhotosTable(this);
  late final $SyncQueueTable syncQueue = $SyncQueueTable(this);
  late final $AuditLogTable auditLog = $AuditLogTable(this);
  late final $DeviceSettingsTable deviceSettings = $DeviceSettingsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
        sessions,
        dropdownConfig,
        boundaryZones,
        streets,
        buildings,
        photos,
        syncQueue,
        auditLog,
        deviceSettings
      ];
}

typedef $$SessionsTableCreateCompanionBuilder = SessionsCompanion Function({
  Value<int> id,
  required String userId,
  required String username,
  required String role,
  Value<String?> lgaCode,
  Value<String?> ward,
  required String accessToken,
  required String refreshToken,
  required int tokenExpiresAt,
  Value<int> createdAt,
  Value<String?> passwordHash,
});
typedef $$SessionsTableUpdateCompanionBuilder = SessionsCompanion Function({
  Value<int> id,
  Value<String> userId,
  Value<String> username,
  Value<String> role,
  Value<String?> lgaCode,
  Value<String?> ward,
  Value<String> accessToken,
  Value<String> refreshToken,
  Value<int> tokenExpiresAt,
  Value<int> createdAt,
  Value<String?> passwordHash,
});

class $$SessionsTableFilterComposer
    extends Composer<_$AppDatabase, $SessionsTable> {
  $$SessionsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get userId => $composableBuilder(
      column: $table.userId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get username => $composableBuilder(
      column: $table.username, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get role => $composableBuilder(
      column: $table.role, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get lgaCode => $composableBuilder(
      column: $table.lgaCode, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get ward => $composableBuilder(
      column: $table.ward, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get accessToken => $composableBuilder(
      column: $table.accessToken, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get refreshToken => $composableBuilder(
      column: $table.refreshToken, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get tokenExpiresAt => $composableBuilder(
      column: $table.tokenExpiresAt,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get passwordHash => $composableBuilder(
      column: $table.passwordHash, builder: (column) => ColumnFilters(column));
}

class $$SessionsTableOrderingComposer
    extends Composer<_$AppDatabase, $SessionsTable> {
  $$SessionsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get userId => $composableBuilder(
      column: $table.userId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get username => $composableBuilder(
      column: $table.username, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get role => $composableBuilder(
      column: $table.role, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get lgaCode => $composableBuilder(
      column: $table.lgaCode, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get ward => $composableBuilder(
      column: $table.ward, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get accessToken => $composableBuilder(
      column: $table.accessToken, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get refreshToken => $composableBuilder(
      column: $table.refreshToken,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get tokenExpiresAt => $composableBuilder(
      column: $table.tokenExpiresAt,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get passwordHash => $composableBuilder(
      column: $table.passwordHash,
      builder: (column) => ColumnOrderings(column));
}

class $$SessionsTableAnnotationComposer
    extends Composer<_$AppDatabase, $SessionsTable> {
  $$SessionsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get userId =>
      $composableBuilder(column: $table.userId, builder: (column) => column);

  GeneratedColumn<String> get username =>
      $composableBuilder(column: $table.username, builder: (column) => column);

  GeneratedColumn<String> get role =>
      $composableBuilder(column: $table.role, builder: (column) => column);

  GeneratedColumn<String> get lgaCode =>
      $composableBuilder(column: $table.lgaCode, builder: (column) => column);

  GeneratedColumn<String> get ward =>
      $composableBuilder(column: $table.ward, builder: (column) => column);

  GeneratedColumn<String> get accessToken => $composableBuilder(
      column: $table.accessToken, builder: (column) => column);

  GeneratedColumn<String> get refreshToken => $composableBuilder(
      column: $table.refreshToken, builder: (column) => column);

  GeneratedColumn<int> get tokenExpiresAt => $composableBuilder(
      column: $table.tokenExpiresAt, builder: (column) => column);

  GeneratedColumn<int> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<String> get passwordHash => $composableBuilder(
      column: $table.passwordHash, builder: (column) => column);
}

class $$SessionsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $SessionsTable,
    Session,
    $$SessionsTableFilterComposer,
    $$SessionsTableOrderingComposer,
    $$SessionsTableAnnotationComposer,
    $$SessionsTableCreateCompanionBuilder,
    $$SessionsTableUpdateCompanionBuilder,
    (Session, BaseReferences<_$AppDatabase, $SessionsTable, Session>),
    Session,
    PrefetchHooks Function()> {
  $$SessionsTableTableManager(_$AppDatabase db, $SessionsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SessionsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SessionsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SessionsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> userId = const Value.absent(),
            Value<String> username = const Value.absent(),
            Value<String> role = const Value.absent(),
            Value<String?> lgaCode = const Value.absent(),
            Value<String?> ward = const Value.absent(),
            Value<String> accessToken = const Value.absent(),
            Value<String> refreshToken = const Value.absent(),
            Value<int> tokenExpiresAt = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
            Value<String?> passwordHash = const Value.absent(),
          }) =>
              SessionsCompanion(
            id: id,
            userId: userId,
            username: username,
            role: role,
            lgaCode: lgaCode,
            ward: ward,
            accessToken: accessToken,
            refreshToken: refreshToken,
            tokenExpiresAt: tokenExpiresAt,
            createdAt: createdAt,
            passwordHash: passwordHash,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String userId,
            required String username,
            required String role,
            Value<String?> lgaCode = const Value.absent(),
            Value<String?> ward = const Value.absent(),
            required String accessToken,
            required String refreshToken,
            required int tokenExpiresAt,
            Value<int> createdAt = const Value.absent(),
            Value<String?> passwordHash = const Value.absent(),
          }) =>
              SessionsCompanion.insert(
            id: id,
            userId: userId,
            username: username,
            role: role,
            lgaCode: lgaCode,
            ward: ward,
            accessToken: accessToken,
            refreshToken: refreshToken,
            tokenExpiresAt: tokenExpiresAt,
            createdAt: createdAt,
            passwordHash: passwordHash,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$SessionsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $SessionsTable,
    Session,
    $$SessionsTableFilterComposer,
    $$SessionsTableOrderingComposer,
    $$SessionsTableAnnotationComposer,
    $$SessionsTableCreateCompanionBuilder,
    $$SessionsTableUpdateCompanionBuilder,
    (Session, BaseReferences<_$AppDatabase, $SessionsTable, Session>),
    Session,
    PrefetchHooks Function()>;
typedef $$DropdownConfigTableCreateCompanionBuilder = DropdownConfigCompanion
    Function({
  Value<int> id,
  required String category,
  required String value,
  required String label,
  Value<int> sortOrder,
  Value<int> version,
  Value<int> syncedAt,
});
typedef $$DropdownConfigTableUpdateCompanionBuilder = DropdownConfigCompanion
    Function({
  Value<int> id,
  Value<String> category,
  Value<String> value,
  Value<String> label,
  Value<int> sortOrder,
  Value<int> version,
  Value<int> syncedAt,
});

class $$DropdownConfigTableFilterComposer
    extends Composer<_$AppDatabase, $DropdownConfigTable> {
  $$DropdownConfigTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get category => $composableBuilder(
      column: $table.category, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get value => $composableBuilder(
      column: $table.value, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get label => $composableBuilder(
      column: $table.label, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get sortOrder => $composableBuilder(
      column: $table.sortOrder, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get version => $composableBuilder(
      column: $table.version, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get syncedAt => $composableBuilder(
      column: $table.syncedAt, builder: (column) => ColumnFilters(column));
}

class $$DropdownConfigTableOrderingComposer
    extends Composer<_$AppDatabase, $DropdownConfigTable> {
  $$DropdownConfigTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get category => $composableBuilder(
      column: $table.category, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get value => $composableBuilder(
      column: $table.value, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get label => $composableBuilder(
      column: $table.label, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get sortOrder => $composableBuilder(
      column: $table.sortOrder, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get version => $composableBuilder(
      column: $table.version, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get syncedAt => $composableBuilder(
      column: $table.syncedAt, builder: (column) => ColumnOrderings(column));
}

class $$DropdownConfigTableAnnotationComposer
    extends Composer<_$AppDatabase, $DropdownConfigTable> {
  $$DropdownConfigTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get category =>
      $composableBuilder(column: $table.category, builder: (column) => column);

  GeneratedColumn<String> get value =>
      $composableBuilder(column: $table.value, builder: (column) => column);

  GeneratedColumn<String> get label =>
      $composableBuilder(column: $table.label, builder: (column) => column);

  GeneratedColumn<int> get sortOrder =>
      $composableBuilder(column: $table.sortOrder, builder: (column) => column);

  GeneratedColumn<int> get version =>
      $composableBuilder(column: $table.version, builder: (column) => column);

  GeneratedColumn<int> get syncedAt =>
      $composableBuilder(column: $table.syncedAt, builder: (column) => column);
}

class $$DropdownConfigTableTableManager extends RootTableManager<
    _$AppDatabase,
    $DropdownConfigTable,
    DropdownConfigData,
    $$DropdownConfigTableFilterComposer,
    $$DropdownConfigTableOrderingComposer,
    $$DropdownConfigTableAnnotationComposer,
    $$DropdownConfigTableCreateCompanionBuilder,
    $$DropdownConfigTableUpdateCompanionBuilder,
    (
      DropdownConfigData,
      BaseReferences<_$AppDatabase, $DropdownConfigTable, DropdownConfigData>
    ),
    DropdownConfigData,
    PrefetchHooks Function()> {
  $$DropdownConfigTableTableManager(
      _$AppDatabase db, $DropdownConfigTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$DropdownConfigTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$DropdownConfigTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$DropdownConfigTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> category = const Value.absent(),
            Value<String> value = const Value.absent(),
            Value<String> label = const Value.absent(),
            Value<int> sortOrder = const Value.absent(),
            Value<int> version = const Value.absent(),
            Value<int> syncedAt = const Value.absent(),
          }) =>
              DropdownConfigCompanion(
            id: id,
            category: category,
            value: value,
            label: label,
            sortOrder: sortOrder,
            version: version,
            syncedAt: syncedAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String category,
            required String value,
            required String label,
            Value<int> sortOrder = const Value.absent(),
            Value<int> version = const Value.absent(),
            Value<int> syncedAt = const Value.absent(),
          }) =>
              DropdownConfigCompanion.insert(
            id: id,
            category: category,
            value: value,
            label: label,
            sortOrder: sortOrder,
            version: version,
            syncedAt: syncedAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$DropdownConfigTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $DropdownConfigTable,
    DropdownConfigData,
    $$DropdownConfigTableFilterComposer,
    $$DropdownConfigTableOrderingComposer,
    $$DropdownConfigTableAnnotationComposer,
    $$DropdownConfigTableCreateCompanionBuilder,
    $$DropdownConfigTableUpdateCompanionBuilder,
    (
      DropdownConfigData,
      BaseReferences<_$AppDatabase, $DropdownConfigTable, DropdownConfigData>
    ),
    DropdownConfigData,
    PrefetchHooks Function()>;
typedef $$BoundaryZonesTableCreateCompanionBuilder = BoundaryZonesCompanion
    Function({
  Value<int> id,
  required String zoneId,
  required String zoneName,
  required String zoneType,
  Value<String?> lgaCode,
  Value<String?> wardCode,
  Value<String?> postcode,
  required Uint8List geometryWkb,
  required String shapefileVersion,
  Value<int> createdAt,
});
typedef $$BoundaryZonesTableUpdateCompanionBuilder = BoundaryZonesCompanion
    Function({
  Value<int> id,
  Value<String> zoneId,
  Value<String> zoneName,
  Value<String> zoneType,
  Value<String?> lgaCode,
  Value<String?> wardCode,
  Value<String?> postcode,
  Value<Uint8List> geometryWkb,
  Value<String> shapefileVersion,
  Value<int> createdAt,
});

class $$BoundaryZonesTableFilterComposer
    extends Composer<_$AppDatabase, $BoundaryZonesTable> {
  $$BoundaryZonesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get zoneId => $composableBuilder(
      column: $table.zoneId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get zoneName => $composableBuilder(
      column: $table.zoneName, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get zoneType => $composableBuilder(
      column: $table.zoneType, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get lgaCode => $composableBuilder(
      column: $table.lgaCode, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get wardCode => $composableBuilder(
      column: $table.wardCode, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get postcode => $composableBuilder(
      column: $table.postcode, builder: (column) => ColumnFilters(column));

  ColumnFilters<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get shapefileVersion => $composableBuilder(
      column: $table.shapefileVersion,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$BoundaryZonesTableOrderingComposer
    extends Composer<_$AppDatabase, $BoundaryZonesTable> {
  $$BoundaryZonesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get zoneId => $composableBuilder(
      column: $table.zoneId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get zoneName => $composableBuilder(
      column: $table.zoneName, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get zoneType => $composableBuilder(
      column: $table.zoneType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get lgaCode => $composableBuilder(
      column: $table.lgaCode, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get wardCode => $composableBuilder(
      column: $table.wardCode, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get postcode => $composableBuilder(
      column: $table.postcode, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get shapefileVersion => $composableBuilder(
      column: $table.shapefileVersion,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$BoundaryZonesTableAnnotationComposer
    extends Composer<_$AppDatabase, $BoundaryZonesTable> {
  $$BoundaryZonesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get zoneId =>
      $composableBuilder(column: $table.zoneId, builder: (column) => column);

  GeneratedColumn<String> get zoneName =>
      $composableBuilder(column: $table.zoneName, builder: (column) => column);

  GeneratedColumn<String> get zoneType =>
      $composableBuilder(column: $table.zoneType, builder: (column) => column);

  GeneratedColumn<String> get lgaCode =>
      $composableBuilder(column: $table.lgaCode, builder: (column) => column);

  GeneratedColumn<String> get wardCode =>
      $composableBuilder(column: $table.wardCode, builder: (column) => column);

  GeneratedColumn<String> get postcode =>
      $composableBuilder(column: $table.postcode, builder: (column) => column);

  GeneratedColumn<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => column);

  GeneratedColumn<String> get shapefileVersion => $composableBuilder(
      column: $table.shapefileVersion, builder: (column) => column);

  GeneratedColumn<int> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$BoundaryZonesTableTableManager extends RootTableManager<
    _$AppDatabase,
    $BoundaryZonesTable,
    BoundaryZone,
    $$BoundaryZonesTableFilterComposer,
    $$BoundaryZonesTableOrderingComposer,
    $$BoundaryZonesTableAnnotationComposer,
    $$BoundaryZonesTableCreateCompanionBuilder,
    $$BoundaryZonesTableUpdateCompanionBuilder,
    (
      BoundaryZone,
      BaseReferences<_$AppDatabase, $BoundaryZonesTable, BoundaryZone>
    ),
    BoundaryZone,
    PrefetchHooks Function()> {
  $$BoundaryZonesTableTableManager(_$AppDatabase db, $BoundaryZonesTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$BoundaryZonesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$BoundaryZonesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$BoundaryZonesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> zoneId = const Value.absent(),
            Value<String> zoneName = const Value.absent(),
            Value<String> zoneType = const Value.absent(),
            Value<String?> lgaCode = const Value.absent(),
            Value<String?> wardCode = const Value.absent(),
            Value<String?> postcode = const Value.absent(),
            Value<Uint8List> geometryWkb = const Value.absent(),
            Value<String> shapefileVersion = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              BoundaryZonesCompanion(
            id: id,
            zoneId: zoneId,
            zoneName: zoneName,
            zoneType: zoneType,
            lgaCode: lgaCode,
            wardCode: wardCode,
            postcode: postcode,
            geometryWkb: geometryWkb,
            shapefileVersion: shapefileVersion,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String zoneId,
            required String zoneName,
            required String zoneType,
            Value<String?> lgaCode = const Value.absent(),
            Value<String?> wardCode = const Value.absent(),
            Value<String?> postcode = const Value.absent(),
            required Uint8List geometryWkb,
            required String shapefileVersion,
            Value<int> createdAt = const Value.absent(),
          }) =>
              BoundaryZonesCompanion.insert(
            id: id,
            zoneId: zoneId,
            zoneName: zoneName,
            zoneType: zoneType,
            lgaCode: lgaCode,
            wardCode: wardCode,
            postcode: postcode,
            geometryWkb: geometryWkb,
            shapefileVersion: shapefileVersion,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$BoundaryZonesTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $BoundaryZonesTable,
    BoundaryZone,
    $$BoundaryZonesTableFilterComposer,
    $$BoundaryZonesTableOrderingComposer,
    $$BoundaryZonesTableAnnotationComposer,
    $$BoundaryZonesTableCreateCompanionBuilder,
    $$BoundaryZonesTableUpdateCompanionBuilder,
    (
      BoundaryZone,
      BaseReferences<_$AppDatabase, $BoundaryZonesTable, BoundaryZone>
    ),
    BoundaryZone,
    PrefetchHooks Function()>;
typedef $$StreetsTableCreateCompanionBuilder = StreetsCompanion Function({
  Value<int> id,
  required String streetId,
  required String streetName,
  Value<String> streetAddress,
  required String streetType,
  required String surfaceType,
  required String streetCondition,
  Value<String?> notes,
  required Uint8List geometryWkb,
  Value<String?> zone,
  required String lga,
  Value<String?> ward,
  required String enumeratorId,
  required int enumerationDate,
  Value<String> verificationStatus,
  Value<int> boundaryFlag,
  Value<int> gpsAccuracyFlag,
  Value<String?> qaFlags,
  Value<String?> serverId,
  Value<String> syncStatus,
  Value<int> lastModifiedAt,
  Value<int> createdAt,
});
typedef $$StreetsTableUpdateCompanionBuilder = StreetsCompanion Function({
  Value<int> id,
  Value<String> streetId,
  Value<String> streetName,
  Value<String> streetAddress,
  Value<String> streetType,
  Value<String> surfaceType,
  Value<String> streetCondition,
  Value<String?> notes,
  Value<Uint8List> geometryWkb,
  Value<String?> zone,
  Value<String> lga,
  Value<String?> ward,
  Value<String> enumeratorId,
  Value<int> enumerationDate,
  Value<String> verificationStatus,
  Value<int> boundaryFlag,
  Value<int> gpsAccuracyFlag,
  Value<String?> qaFlags,
  Value<String?> serverId,
  Value<String> syncStatus,
  Value<int> lastModifiedAt,
  Value<int> createdAt,
});

class $$StreetsTableFilterComposer
    extends Composer<_$AppDatabase, $StreetsTable> {
  $$StreetsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get streetId => $composableBuilder(
      column: $table.streetId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get streetName => $composableBuilder(
      column: $table.streetName, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get streetAddress => $composableBuilder(
      column: $table.streetAddress, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get streetType => $composableBuilder(
      column: $table.streetType, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get surfaceType => $composableBuilder(
      column: $table.surfaceType, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get streetCondition => $composableBuilder(
      column: $table.streetCondition,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get notes => $composableBuilder(
      column: $table.notes, builder: (column) => ColumnFilters(column));

  ColumnFilters<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get zone => $composableBuilder(
      column: $table.zone, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get lga => $composableBuilder(
      column: $table.lga, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get ward => $composableBuilder(
      column: $table.ward, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get enumeratorId => $composableBuilder(
      column: $table.enumeratorId, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get enumerationDate => $composableBuilder(
      column: $table.enumerationDate,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get verificationStatus => $composableBuilder(
      column: $table.verificationStatus,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get boundaryFlag => $composableBuilder(
      column: $table.boundaryFlag, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get gpsAccuracyFlag => $composableBuilder(
      column: $table.gpsAccuracyFlag,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get qaFlags => $composableBuilder(
      column: $table.qaFlags, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get lastModifiedAt => $composableBuilder(
      column: $table.lastModifiedAt,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$StreetsTableOrderingComposer
    extends Composer<_$AppDatabase, $StreetsTable> {
  $$StreetsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get streetId => $composableBuilder(
      column: $table.streetId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get streetName => $composableBuilder(
      column: $table.streetName, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get streetAddress => $composableBuilder(
      column: $table.streetAddress,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get streetType => $composableBuilder(
      column: $table.streetType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get surfaceType => $composableBuilder(
      column: $table.surfaceType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get streetCondition => $composableBuilder(
      column: $table.streetCondition,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get notes => $composableBuilder(
      column: $table.notes, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get zone => $composableBuilder(
      column: $table.zone, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get lga => $composableBuilder(
      column: $table.lga, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get ward => $composableBuilder(
      column: $table.ward, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get enumeratorId => $composableBuilder(
      column: $table.enumeratorId,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get enumerationDate => $composableBuilder(
      column: $table.enumerationDate,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get verificationStatus => $composableBuilder(
      column: $table.verificationStatus,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get boundaryFlag => $composableBuilder(
      column: $table.boundaryFlag,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get gpsAccuracyFlag => $composableBuilder(
      column: $table.gpsAccuracyFlag,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get qaFlags => $composableBuilder(
      column: $table.qaFlags, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get lastModifiedAt => $composableBuilder(
      column: $table.lastModifiedAt,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$StreetsTableAnnotationComposer
    extends Composer<_$AppDatabase, $StreetsTable> {
  $$StreetsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get streetId =>
      $composableBuilder(column: $table.streetId, builder: (column) => column);

  GeneratedColumn<String> get streetName => $composableBuilder(
      column: $table.streetName, builder: (column) => column);

  GeneratedColumn<String> get streetAddress => $composableBuilder(
      column: $table.streetAddress, builder: (column) => column);

  GeneratedColumn<String> get streetType => $composableBuilder(
      column: $table.streetType, builder: (column) => column);

  GeneratedColumn<String> get surfaceType => $composableBuilder(
      column: $table.surfaceType, builder: (column) => column);

  GeneratedColumn<String> get streetCondition => $composableBuilder(
      column: $table.streetCondition, builder: (column) => column);

  GeneratedColumn<String> get notes =>
      $composableBuilder(column: $table.notes, builder: (column) => column);

  GeneratedColumn<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => column);

  GeneratedColumn<String> get zone =>
      $composableBuilder(column: $table.zone, builder: (column) => column);

  GeneratedColumn<String> get lga =>
      $composableBuilder(column: $table.lga, builder: (column) => column);

  GeneratedColumn<String> get ward =>
      $composableBuilder(column: $table.ward, builder: (column) => column);

  GeneratedColumn<String> get enumeratorId => $composableBuilder(
      column: $table.enumeratorId, builder: (column) => column);

  GeneratedColumn<int> get enumerationDate => $composableBuilder(
      column: $table.enumerationDate, builder: (column) => column);

  GeneratedColumn<String> get verificationStatus => $composableBuilder(
      column: $table.verificationStatus, builder: (column) => column);

  GeneratedColumn<int> get boundaryFlag => $composableBuilder(
      column: $table.boundaryFlag, builder: (column) => column);

  GeneratedColumn<int> get gpsAccuracyFlag => $composableBuilder(
      column: $table.gpsAccuracyFlag, builder: (column) => column);

  GeneratedColumn<String> get qaFlags =>
      $composableBuilder(column: $table.qaFlags, builder: (column) => column);

  GeneratedColumn<String> get serverId =>
      $composableBuilder(column: $table.serverId, builder: (column) => column);

  GeneratedColumn<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => column);

  GeneratedColumn<int> get lastModifiedAt => $composableBuilder(
      column: $table.lastModifiedAt, builder: (column) => column);

  GeneratedColumn<int> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$StreetsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $StreetsTable,
    Street,
    $$StreetsTableFilterComposer,
    $$StreetsTableOrderingComposer,
    $$StreetsTableAnnotationComposer,
    $$StreetsTableCreateCompanionBuilder,
    $$StreetsTableUpdateCompanionBuilder,
    (Street, BaseReferences<_$AppDatabase, $StreetsTable, Street>),
    Street,
    PrefetchHooks Function()> {
  $$StreetsTableTableManager(_$AppDatabase db, $StreetsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$StreetsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$StreetsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$StreetsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> streetId = const Value.absent(),
            Value<String> streetName = const Value.absent(),
            Value<String> streetAddress = const Value.absent(),
            Value<String> streetType = const Value.absent(),
            Value<String> surfaceType = const Value.absent(),
            Value<String> streetCondition = const Value.absent(),
            Value<String?> notes = const Value.absent(),
            Value<Uint8List> geometryWkb = const Value.absent(),
            Value<String?> zone = const Value.absent(),
            Value<String> lga = const Value.absent(),
            Value<String?> ward = const Value.absent(),
            Value<String> enumeratorId = const Value.absent(),
            Value<int> enumerationDate = const Value.absent(),
            Value<String> verificationStatus = const Value.absent(),
            Value<int> boundaryFlag = const Value.absent(),
            Value<int> gpsAccuracyFlag = const Value.absent(),
            Value<String?> qaFlags = const Value.absent(),
            Value<String?> serverId = const Value.absent(),
            Value<String> syncStatus = const Value.absent(),
            Value<int> lastModifiedAt = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              StreetsCompanion(
            id: id,
            streetId: streetId,
            streetName: streetName,
            streetAddress: streetAddress,
            streetType: streetType,
            surfaceType: surfaceType,
            streetCondition: streetCondition,
            notes: notes,
            geometryWkb: geometryWkb,
            zone: zone,
            lga: lga,
            ward: ward,
            enumeratorId: enumeratorId,
            enumerationDate: enumerationDate,
            verificationStatus: verificationStatus,
            boundaryFlag: boundaryFlag,
            gpsAccuracyFlag: gpsAccuracyFlag,
            qaFlags: qaFlags,
            serverId: serverId,
            syncStatus: syncStatus,
            lastModifiedAt: lastModifiedAt,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String streetId,
            required String streetName,
            Value<String> streetAddress = const Value.absent(),
            required String streetType,
            required String surfaceType,
            required String streetCondition,
            Value<String?> notes = const Value.absent(),
            required Uint8List geometryWkb,
            Value<String?> zone = const Value.absent(),
            required String lga,
            Value<String?> ward = const Value.absent(),
            required String enumeratorId,
            required int enumerationDate,
            Value<String> verificationStatus = const Value.absent(),
            Value<int> boundaryFlag = const Value.absent(),
            Value<int> gpsAccuracyFlag = const Value.absent(),
            Value<String?> qaFlags = const Value.absent(),
            Value<String?> serverId = const Value.absent(),
            Value<String> syncStatus = const Value.absent(),
            Value<int> lastModifiedAt = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              StreetsCompanion.insert(
            id: id,
            streetId: streetId,
            streetName: streetName,
            streetAddress: streetAddress,
            streetType: streetType,
            surfaceType: surfaceType,
            streetCondition: streetCondition,
            notes: notes,
            geometryWkb: geometryWkb,
            zone: zone,
            lga: lga,
            ward: ward,
            enumeratorId: enumeratorId,
            enumerationDate: enumerationDate,
            verificationStatus: verificationStatus,
            boundaryFlag: boundaryFlag,
            gpsAccuracyFlag: gpsAccuracyFlag,
            qaFlags: qaFlags,
            serverId: serverId,
            syncStatus: syncStatus,
            lastModifiedAt: lastModifiedAt,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$StreetsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $StreetsTable,
    Street,
    $$StreetsTableFilterComposer,
    $$StreetsTableOrderingComposer,
    $$StreetsTableAnnotationComposer,
    $$StreetsTableCreateCompanionBuilder,
    $$StreetsTableUpdateCompanionBuilder,
    (Street, BaseReferences<_$AppDatabase, $StreetsTable, Street>),
    Street,
    PrefetchHooks Function()>;
typedef $$BuildingsTableCreateCompanionBuilder = BuildingsCompanion Function({
  Value<int> id,
  required String buildingId,
  required String streetId,
  required String buildingType,
  required int numberOfFloors,
  required int numberOfUnits,
  required String buildingCondition,
  Value<String?> streetAddress,
  Value<int> hasSignage,
  Value<String?> businessNames,
  Value<String?> notes,
  required Uint8List geometryWkb,
  required double gpsAccuracyM,
  Value<String?> zone,
  required String lga,
  Value<String?> ward,
  Value<String?> postcode,
  Value<String> postcodeStatus,
  required String enumeratorId,
  required int enumerationDate,
  Value<String> verificationStatus,
  Value<String?> rejectionReason,
  Value<String?> disputeReason,
  Value<String?> verifiedBy,
  Value<int?> verifiedAt,
  Value<int> boundaryFlag,
  Value<int> gpsAccuracyFlag,
  Value<int> duplicateFlag,
  Value<String?> qaFlags,
  Value<String?> serverId,
  Value<String> syncStatus,
  Value<int> lastModifiedAt,
  Value<int> createdAt,
});
typedef $$BuildingsTableUpdateCompanionBuilder = BuildingsCompanion Function({
  Value<int> id,
  Value<String> buildingId,
  Value<String> streetId,
  Value<String> buildingType,
  Value<int> numberOfFloors,
  Value<int> numberOfUnits,
  Value<String> buildingCondition,
  Value<String?> streetAddress,
  Value<int> hasSignage,
  Value<String?> businessNames,
  Value<String?> notes,
  Value<Uint8List> geometryWkb,
  Value<double> gpsAccuracyM,
  Value<String?> zone,
  Value<String> lga,
  Value<String?> ward,
  Value<String?> postcode,
  Value<String> postcodeStatus,
  Value<String> enumeratorId,
  Value<int> enumerationDate,
  Value<String> verificationStatus,
  Value<String?> rejectionReason,
  Value<String?> disputeReason,
  Value<String?> verifiedBy,
  Value<int?> verifiedAt,
  Value<int> boundaryFlag,
  Value<int> gpsAccuracyFlag,
  Value<int> duplicateFlag,
  Value<String?> qaFlags,
  Value<String?> serverId,
  Value<String> syncStatus,
  Value<int> lastModifiedAt,
  Value<int> createdAt,
});

class $$BuildingsTableFilterComposer
    extends Composer<_$AppDatabase, $BuildingsTable> {
  $$BuildingsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get buildingId => $composableBuilder(
      column: $table.buildingId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get streetId => $composableBuilder(
      column: $table.streetId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get buildingType => $composableBuilder(
      column: $table.buildingType, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get numberOfFloors => $composableBuilder(
      column: $table.numberOfFloors,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get numberOfUnits => $composableBuilder(
      column: $table.numberOfUnits, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get buildingCondition => $composableBuilder(
      column: $table.buildingCondition,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get streetAddress => $composableBuilder(
      column: $table.streetAddress, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get hasSignage => $composableBuilder(
      column: $table.hasSignage, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get businessNames => $composableBuilder(
      column: $table.businessNames, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get notes => $composableBuilder(
      column: $table.notes, builder: (column) => ColumnFilters(column));

  ColumnFilters<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get gpsAccuracyM => $composableBuilder(
      column: $table.gpsAccuracyM, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get zone => $composableBuilder(
      column: $table.zone, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get lga => $composableBuilder(
      column: $table.lga, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get ward => $composableBuilder(
      column: $table.ward, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get postcode => $composableBuilder(
      column: $table.postcode, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get postcodeStatus => $composableBuilder(
      column: $table.postcodeStatus,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get enumeratorId => $composableBuilder(
      column: $table.enumeratorId, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get enumerationDate => $composableBuilder(
      column: $table.enumerationDate,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get verificationStatus => $composableBuilder(
      column: $table.verificationStatus,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get rejectionReason => $composableBuilder(
      column: $table.rejectionReason,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get disputeReason => $composableBuilder(
      column: $table.disputeReason, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get verifiedBy => $composableBuilder(
      column: $table.verifiedBy, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get verifiedAt => $composableBuilder(
      column: $table.verifiedAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get boundaryFlag => $composableBuilder(
      column: $table.boundaryFlag, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get gpsAccuracyFlag => $composableBuilder(
      column: $table.gpsAccuracyFlag,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get duplicateFlag => $composableBuilder(
      column: $table.duplicateFlag, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get qaFlags => $composableBuilder(
      column: $table.qaFlags, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get lastModifiedAt => $composableBuilder(
      column: $table.lastModifiedAt,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$BuildingsTableOrderingComposer
    extends Composer<_$AppDatabase, $BuildingsTable> {
  $$BuildingsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get buildingId => $composableBuilder(
      column: $table.buildingId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get streetId => $composableBuilder(
      column: $table.streetId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get buildingType => $composableBuilder(
      column: $table.buildingType,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get numberOfFloors => $composableBuilder(
      column: $table.numberOfFloors,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get numberOfUnits => $composableBuilder(
      column: $table.numberOfUnits,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get buildingCondition => $composableBuilder(
      column: $table.buildingCondition,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get streetAddress => $composableBuilder(
      column: $table.streetAddress,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get hasSignage => $composableBuilder(
      column: $table.hasSignage, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get businessNames => $composableBuilder(
      column: $table.businessNames,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get notes => $composableBuilder(
      column: $table.notes, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get gpsAccuracyM => $composableBuilder(
      column: $table.gpsAccuracyM,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get zone => $composableBuilder(
      column: $table.zone, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get lga => $composableBuilder(
      column: $table.lga, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get ward => $composableBuilder(
      column: $table.ward, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get postcode => $composableBuilder(
      column: $table.postcode, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get postcodeStatus => $composableBuilder(
      column: $table.postcodeStatus,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get enumeratorId => $composableBuilder(
      column: $table.enumeratorId,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get enumerationDate => $composableBuilder(
      column: $table.enumerationDate,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get verificationStatus => $composableBuilder(
      column: $table.verificationStatus,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get rejectionReason => $composableBuilder(
      column: $table.rejectionReason,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get disputeReason => $composableBuilder(
      column: $table.disputeReason,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get verifiedBy => $composableBuilder(
      column: $table.verifiedBy, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get verifiedAt => $composableBuilder(
      column: $table.verifiedAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get boundaryFlag => $composableBuilder(
      column: $table.boundaryFlag,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get gpsAccuracyFlag => $composableBuilder(
      column: $table.gpsAccuracyFlag,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get duplicateFlag => $composableBuilder(
      column: $table.duplicateFlag,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get qaFlags => $composableBuilder(
      column: $table.qaFlags, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get lastModifiedAt => $composableBuilder(
      column: $table.lastModifiedAt,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$BuildingsTableAnnotationComposer
    extends Composer<_$AppDatabase, $BuildingsTable> {
  $$BuildingsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get buildingId => $composableBuilder(
      column: $table.buildingId, builder: (column) => column);

  GeneratedColumn<String> get streetId =>
      $composableBuilder(column: $table.streetId, builder: (column) => column);

  GeneratedColumn<String> get buildingType => $composableBuilder(
      column: $table.buildingType, builder: (column) => column);

  GeneratedColumn<int> get numberOfFloors => $composableBuilder(
      column: $table.numberOfFloors, builder: (column) => column);

  GeneratedColumn<int> get numberOfUnits => $composableBuilder(
      column: $table.numberOfUnits, builder: (column) => column);

  GeneratedColumn<String> get buildingCondition => $composableBuilder(
      column: $table.buildingCondition, builder: (column) => column);

  GeneratedColumn<String> get streetAddress => $composableBuilder(
      column: $table.streetAddress, builder: (column) => column);

  GeneratedColumn<int> get hasSignage => $composableBuilder(
      column: $table.hasSignage, builder: (column) => column);

  GeneratedColumn<String> get businessNames => $composableBuilder(
      column: $table.businessNames, builder: (column) => column);

  GeneratedColumn<String> get notes =>
      $composableBuilder(column: $table.notes, builder: (column) => column);

  GeneratedColumn<Uint8List> get geometryWkb => $composableBuilder(
      column: $table.geometryWkb, builder: (column) => column);

  GeneratedColumn<double> get gpsAccuracyM => $composableBuilder(
      column: $table.gpsAccuracyM, builder: (column) => column);

  GeneratedColumn<String> get zone =>
      $composableBuilder(column: $table.zone, builder: (column) => column);

  GeneratedColumn<String> get lga =>
      $composableBuilder(column: $table.lga, builder: (column) => column);

  GeneratedColumn<String> get ward =>
      $composableBuilder(column: $table.ward, builder: (column) => column);

  GeneratedColumn<String> get postcode =>
      $composableBuilder(column: $table.postcode, builder: (column) => column);

  GeneratedColumn<String> get postcodeStatus => $composableBuilder(
      column: $table.postcodeStatus, builder: (column) => column);

  GeneratedColumn<String> get enumeratorId => $composableBuilder(
      column: $table.enumeratorId, builder: (column) => column);

  GeneratedColumn<int> get enumerationDate => $composableBuilder(
      column: $table.enumerationDate, builder: (column) => column);

  GeneratedColumn<String> get verificationStatus => $composableBuilder(
      column: $table.verificationStatus, builder: (column) => column);

  GeneratedColumn<String> get rejectionReason => $composableBuilder(
      column: $table.rejectionReason, builder: (column) => column);

  GeneratedColumn<String> get disputeReason => $composableBuilder(
      column: $table.disputeReason, builder: (column) => column);

  GeneratedColumn<String> get verifiedBy => $composableBuilder(
      column: $table.verifiedBy, builder: (column) => column);

  GeneratedColumn<int> get verifiedAt => $composableBuilder(
      column: $table.verifiedAt, builder: (column) => column);

  GeneratedColumn<int> get boundaryFlag => $composableBuilder(
      column: $table.boundaryFlag, builder: (column) => column);

  GeneratedColumn<int> get gpsAccuracyFlag => $composableBuilder(
      column: $table.gpsAccuracyFlag, builder: (column) => column);

  GeneratedColumn<int> get duplicateFlag => $composableBuilder(
      column: $table.duplicateFlag, builder: (column) => column);

  GeneratedColumn<String> get qaFlags =>
      $composableBuilder(column: $table.qaFlags, builder: (column) => column);

  GeneratedColumn<String> get serverId =>
      $composableBuilder(column: $table.serverId, builder: (column) => column);

  GeneratedColumn<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => column);

  GeneratedColumn<int> get lastModifiedAt => $composableBuilder(
      column: $table.lastModifiedAt, builder: (column) => column);

  GeneratedColumn<int> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$BuildingsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $BuildingsTable,
    Building,
    $$BuildingsTableFilterComposer,
    $$BuildingsTableOrderingComposer,
    $$BuildingsTableAnnotationComposer,
    $$BuildingsTableCreateCompanionBuilder,
    $$BuildingsTableUpdateCompanionBuilder,
    (Building, BaseReferences<_$AppDatabase, $BuildingsTable, Building>),
    Building,
    PrefetchHooks Function()> {
  $$BuildingsTableTableManager(_$AppDatabase db, $BuildingsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$BuildingsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$BuildingsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$BuildingsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> buildingId = const Value.absent(),
            Value<String> streetId = const Value.absent(),
            Value<String> buildingType = const Value.absent(),
            Value<int> numberOfFloors = const Value.absent(),
            Value<int> numberOfUnits = const Value.absent(),
            Value<String> buildingCondition = const Value.absent(),
            Value<String?> streetAddress = const Value.absent(),
            Value<int> hasSignage = const Value.absent(),
            Value<String?> businessNames = const Value.absent(),
            Value<String?> notes = const Value.absent(),
            Value<Uint8List> geometryWkb = const Value.absent(),
            Value<double> gpsAccuracyM = const Value.absent(),
            Value<String?> zone = const Value.absent(),
            Value<String> lga = const Value.absent(),
            Value<String?> ward = const Value.absent(),
            Value<String?> postcode = const Value.absent(),
            Value<String> postcodeStatus = const Value.absent(),
            Value<String> enumeratorId = const Value.absent(),
            Value<int> enumerationDate = const Value.absent(),
            Value<String> verificationStatus = const Value.absent(),
            Value<String?> rejectionReason = const Value.absent(),
            Value<String?> disputeReason = const Value.absent(),
            Value<String?> verifiedBy = const Value.absent(),
            Value<int?> verifiedAt = const Value.absent(),
            Value<int> boundaryFlag = const Value.absent(),
            Value<int> gpsAccuracyFlag = const Value.absent(),
            Value<int> duplicateFlag = const Value.absent(),
            Value<String?> qaFlags = const Value.absent(),
            Value<String?> serverId = const Value.absent(),
            Value<String> syncStatus = const Value.absent(),
            Value<int> lastModifiedAt = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              BuildingsCompanion(
            id: id,
            buildingId: buildingId,
            streetId: streetId,
            buildingType: buildingType,
            numberOfFloors: numberOfFloors,
            numberOfUnits: numberOfUnits,
            buildingCondition: buildingCondition,
            streetAddress: streetAddress,
            hasSignage: hasSignage,
            businessNames: businessNames,
            notes: notes,
            geometryWkb: geometryWkb,
            gpsAccuracyM: gpsAccuracyM,
            zone: zone,
            lga: lga,
            ward: ward,
            postcode: postcode,
            postcodeStatus: postcodeStatus,
            enumeratorId: enumeratorId,
            enumerationDate: enumerationDate,
            verificationStatus: verificationStatus,
            rejectionReason: rejectionReason,
            disputeReason: disputeReason,
            verifiedBy: verifiedBy,
            verifiedAt: verifiedAt,
            boundaryFlag: boundaryFlag,
            gpsAccuracyFlag: gpsAccuracyFlag,
            duplicateFlag: duplicateFlag,
            qaFlags: qaFlags,
            serverId: serverId,
            syncStatus: syncStatus,
            lastModifiedAt: lastModifiedAt,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String buildingId,
            required String streetId,
            required String buildingType,
            required int numberOfFloors,
            required int numberOfUnits,
            required String buildingCondition,
            Value<String?> streetAddress = const Value.absent(),
            Value<int> hasSignage = const Value.absent(),
            Value<String?> businessNames = const Value.absent(),
            Value<String?> notes = const Value.absent(),
            required Uint8List geometryWkb,
            required double gpsAccuracyM,
            Value<String?> zone = const Value.absent(),
            required String lga,
            Value<String?> ward = const Value.absent(),
            Value<String?> postcode = const Value.absent(),
            Value<String> postcodeStatus = const Value.absent(),
            required String enumeratorId,
            required int enumerationDate,
            Value<String> verificationStatus = const Value.absent(),
            Value<String?> rejectionReason = const Value.absent(),
            Value<String?> disputeReason = const Value.absent(),
            Value<String?> verifiedBy = const Value.absent(),
            Value<int?> verifiedAt = const Value.absent(),
            Value<int> boundaryFlag = const Value.absent(),
            Value<int> gpsAccuracyFlag = const Value.absent(),
            Value<int> duplicateFlag = const Value.absent(),
            Value<String?> qaFlags = const Value.absent(),
            Value<String?> serverId = const Value.absent(),
            Value<String> syncStatus = const Value.absent(),
            Value<int> lastModifiedAt = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              BuildingsCompanion.insert(
            id: id,
            buildingId: buildingId,
            streetId: streetId,
            buildingType: buildingType,
            numberOfFloors: numberOfFloors,
            numberOfUnits: numberOfUnits,
            buildingCondition: buildingCondition,
            streetAddress: streetAddress,
            hasSignage: hasSignage,
            businessNames: businessNames,
            notes: notes,
            geometryWkb: geometryWkb,
            gpsAccuracyM: gpsAccuracyM,
            zone: zone,
            lga: lga,
            ward: ward,
            postcode: postcode,
            postcodeStatus: postcodeStatus,
            enumeratorId: enumeratorId,
            enumerationDate: enumerationDate,
            verificationStatus: verificationStatus,
            rejectionReason: rejectionReason,
            disputeReason: disputeReason,
            verifiedBy: verifiedBy,
            verifiedAt: verifiedAt,
            boundaryFlag: boundaryFlag,
            gpsAccuracyFlag: gpsAccuracyFlag,
            duplicateFlag: duplicateFlag,
            qaFlags: qaFlags,
            serverId: serverId,
            syncStatus: syncStatus,
            lastModifiedAt: lastModifiedAt,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$BuildingsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $BuildingsTable,
    Building,
    $$BuildingsTableFilterComposer,
    $$BuildingsTableOrderingComposer,
    $$BuildingsTableAnnotationComposer,
    $$BuildingsTableCreateCompanionBuilder,
    $$BuildingsTableUpdateCompanionBuilder,
    (Building, BaseReferences<_$AppDatabase, $BuildingsTable, Building>),
    Building,
    PrefetchHooks Function()>;
typedef $$PhotosTableCreateCompanionBuilder = PhotosCompanion Function({
  Value<int> id,
  required String photoId,
  required String recordType,
  required int recordLocalId,
  required String filePath,
  Value<int> isFrontage,
  required double latitude,
  required double longitude,
  required int capturedAt,
  Value<int?> fileSizeBytes,
  Value<int> brokenRefFlag,
  Value<String> syncStatus,
  Value<int> createdAt,
});
typedef $$PhotosTableUpdateCompanionBuilder = PhotosCompanion Function({
  Value<int> id,
  Value<String> photoId,
  Value<String> recordType,
  Value<int> recordLocalId,
  Value<String> filePath,
  Value<int> isFrontage,
  Value<double> latitude,
  Value<double> longitude,
  Value<int> capturedAt,
  Value<int?> fileSizeBytes,
  Value<int> brokenRefFlag,
  Value<String> syncStatus,
  Value<int> createdAt,
});

class $$PhotosTableFilterComposer
    extends Composer<_$AppDatabase, $PhotosTable> {
  $$PhotosTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get photoId => $composableBuilder(
      column: $table.photoId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get recordType => $composableBuilder(
      column: $table.recordType, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get recordLocalId => $composableBuilder(
      column: $table.recordLocalId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get filePath => $composableBuilder(
      column: $table.filePath, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get isFrontage => $composableBuilder(
      column: $table.isFrontage, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get latitude => $composableBuilder(
      column: $table.latitude, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get longitude => $composableBuilder(
      column: $table.longitude, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get capturedAt => $composableBuilder(
      column: $table.capturedAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get fileSizeBytes => $composableBuilder(
      column: $table.fileSizeBytes, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get brokenRefFlag => $composableBuilder(
      column: $table.brokenRefFlag, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$PhotosTableOrderingComposer
    extends Composer<_$AppDatabase, $PhotosTable> {
  $$PhotosTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get photoId => $composableBuilder(
      column: $table.photoId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get recordType => $composableBuilder(
      column: $table.recordType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get recordLocalId => $composableBuilder(
      column: $table.recordLocalId,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get filePath => $composableBuilder(
      column: $table.filePath, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get isFrontage => $composableBuilder(
      column: $table.isFrontage, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get latitude => $composableBuilder(
      column: $table.latitude, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get longitude => $composableBuilder(
      column: $table.longitude, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get capturedAt => $composableBuilder(
      column: $table.capturedAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get fileSizeBytes => $composableBuilder(
      column: $table.fileSizeBytes,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get brokenRefFlag => $composableBuilder(
      column: $table.brokenRefFlag,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$PhotosTableAnnotationComposer
    extends Composer<_$AppDatabase, $PhotosTable> {
  $$PhotosTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get photoId =>
      $composableBuilder(column: $table.photoId, builder: (column) => column);

  GeneratedColumn<String> get recordType => $composableBuilder(
      column: $table.recordType, builder: (column) => column);

  GeneratedColumn<int> get recordLocalId => $composableBuilder(
      column: $table.recordLocalId, builder: (column) => column);

  GeneratedColumn<String> get filePath =>
      $composableBuilder(column: $table.filePath, builder: (column) => column);

  GeneratedColumn<int> get isFrontage => $composableBuilder(
      column: $table.isFrontage, builder: (column) => column);

  GeneratedColumn<double> get latitude =>
      $composableBuilder(column: $table.latitude, builder: (column) => column);

  GeneratedColumn<double> get longitude =>
      $composableBuilder(column: $table.longitude, builder: (column) => column);

  GeneratedColumn<int> get capturedAt => $composableBuilder(
      column: $table.capturedAt, builder: (column) => column);

  GeneratedColumn<int> get fileSizeBytes => $composableBuilder(
      column: $table.fileSizeBytes, builder: (column) => column);

  GeneratedColumn<int> get brokenRefFlag => $composableBuilder(
      column: $table.brokenRefFlag, builder: (column) => column);

  GeneratedColumn<String> get syncStatus => $composableBuilder(
      column: $table.syncStatus, builder: (column) => column);

  GeneratedColumn<int> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$PhotosTableTableManager extends RootTableManager<
    _$AppDatabase,
    $PhotosTable,
    Photo,
    $$PhotosTableFilterComposer,
    $$PhotosTableOrderingComposer,
    $$PhotosTableAnnotationComposer,
    $$PhotosTableCreateCompanionBuilder,
    $$PhotosTableUpdateCompanionBuilder,
    (Photo, BaseReferences<_$AppDatabase, $PhotosTable, Photo>),
    Photo,
    PrefetchHooks Function()> {
  $$PhotosTableTableManager(_$AppDatabase db, $PhotosTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PhotosTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PhotosTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PhotosTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> photoId = const Value.absent(),
            Value<String> recordType = const Value.absent(),
            Value<int> recordLocalId = const Value.absent(),
            Value<String> filePath = const Value.absent(),
            Value<int> isFrontage = const Value.absent(),
            Value<double> latitude = const Value.absent(),
            Value<double> longitude = const Value.absent(),
            Value<int> capturedAt = const Value.absent(),
            Value<int?> fileSizeBytes = const Value.absent(),
            Value<int> brokenRefFlag = const Value.absent(),
            Value<String> syncStatus = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              PhotosCompanion(
            id: id,
            photoId: photoId,
            recordType: recordType,
            recordLocalId: recordLocalId,
            filePath: filePath,
            isFrontage: isFrontage,
            latitude: latitude,
            longitude: longitude,
            capturedAt: capturedAt,
            fileSizeBytes: fileSizeBytes,
            brokenRefFlag: brokenRefFlag,
            syncStatus: syncStatus,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String photoId,
            required String recordType,
            required int recordLocalId,
            required String filePath,
            Value<int> isFrontage = const Value.absent(),
            required double latitude,
            required double longitude,
            required int capturedAt,
            Value<int?> fileSizeBytes = const Value.absent(),
            Value<int> brokenRefFlag = const Value.absent(),
            Value<String> syncStatus = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              PhotosCompanion.insert(
            id: id,
            photoId: photoId,
            recordType: recordType,
            recordLocalId: recordLocalId,
            filePath: filePath,
            isFrontage: isFrontage,
            latitude: latitude,
            longitude: longitude,
            capturedAt: capturedAt,
            fileSizeBytes: fileSizeBytes,
            brokenRefFlag: brokenRefFlag,
            syncStatus: syncStatus,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$PhotosTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $PhotosTable,
    Photo,
    $$PhotosTableFilterComposer,
    $$PhotosTableOrderingComposer,
    $$PhotosTableAnnotationComposer,
    $$PhotosTableCreateCompanionBuilder,
    $$PhotosTableUpdateCompanionBuilder,
    (Photo, BaseReferences<_$AppDatabase, $PhotosTable, Photo>),
    Photo,
    PrefetchHooks Function()>;
typedef $$SyncQueueTableCreateCompanionBuilder = SyncQueueCompanion Function({
  Value<int> id,
  required String operation,
  required String entityType,
  required int entityLocalId,
  required String payloadJson,
  Value<int> attemptCount,
  Value<int?> lastAttemptAt,
  Value<String?> lastError,
  Value<String> status,
  Value<int> createdAt,
});
typedef $$SyncQueueTableUpdateCompanionBuilder = SyncQueueCompanion Function({
  Value<int> id,
  Value<String> operation,
  Value<String> entityType,
  Value<int> entityLocalId,
  Value<String> payloadJson,
  Value<int> attemptCount,
  Value<int?> lastAttemptAt,
  Value<String?> lastError,
  Value<String> status,
  Value<int> createdAt,
});

class $$SyncQueueTableFilterComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get operation => $composableBuilder(
      column: $table.operation, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get entityLocalId => $composableBuilder(
      column: $table.entityLocalId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get payloadJson => $composableBuilder(
      column: $table.payloadJson, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get attemptCount => $composableBuilder(
      column: $table.attemptCount, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get lastAttemptAt => $composableBuilder(
      column: $table.lastAttemptAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get lastError => $composableBuilder(
      column: $table.lastError, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$SyncQueueTableOrderingComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get operation => $composableBuilder(
      column: $table.operation, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get entityLocalId => $composableBuilder(
      column: $table.entityLocalId,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get payloadJson => $composableBuilder(
      column: $table.payloadJson, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get attemptCount => $composableBuilder(
      column: $table.attemptCount,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get lastAttemptAt => $composableBuilder(
      column: $table.lastAttemptAt,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get lastError => $composableBuilder(
      column: $table.lastError, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$SyncQueueTableAnnotationComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get operation =>
      $composableBuilder(column: $table.operation, builder: (column) => column);

  GeneratedColumn<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => column);

  GeneratedColumn<int> get entityLocalId => $composableBuilder(
      column: $table.entityLocalId, builder: (column) => column);

  GeneratedColumn<String> get payloadJson => $composableBuilder(
      column: $table.payloadJson, builder: (column) => column);

  GeneratedColumn<int> get attemptCount => $composableBuilder(
      column: $table.attemptCount, builder: (column) => column);

  GeneratedColumn<int> get lastAttemptAt => $composableBuilder(
      column: $table.lastAttemptAt, builder: (column) => column);

  GeneratedColumn<String> get lastError =>
      $composableBuilder(column: $table.lastError, builder: (column) => column);

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<int> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$SyncQueueTableTableManager extends RootTableManager<
    _$AppDatabase,
    $SyncQueueTable,
    SyncQueueData,
    $$SyncQueueTableFilterComposer,
    $$SyncQueueTableOrderingComposer,
    $$SyncQueueTableAnnotationComposer,
    $$SyncQueueTableCreateCompanionBuilder,
    $$SyncQueueTableUpdateCompanionBuilder,
    (
      SyncQueueData,
      BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>
    ),
    SyncQueueData,
    PrefetchHooks Function()> {
  $$SyncQueueTableTableManager(_$AppDatabase db, $SyncQueueTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncQueueTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncQueueTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncQueueTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> operation = const Value.absent(),
            Value<String> entityType = const Value.absent(),
            Value<int> entityLocalId = const Value.absent(),
            Value<String> payloadJson = const Value.absent(),
            Value<int> attemptCount = const Value.absent(),
            Value<int?> lastAttemptAt = const Value.absent(),
            Value<String?> lastError = const Value.absent(),
            Value<String> status = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              SyncQueueCompanion(
            id: id,
            operation: operation,
            entityType: entityType,
            entityLocalId: entityLocalId,
            payloadJson: payloadJson,
            attemptCount: attemptCount,
            lastAttemptAt: lastAttemptAt,
            lastError: lastError,
            status: status,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String operation,
            required String entityType,
            required int entityLocalId,
            required String payloadJson,
            Value<int> attemptCount = const Value.absent(),
            Value<int?> lastAttemptAt = const Value.absent(),
            Value<String?> lastError = const Value.absent(),
            Value<String> status = const Value.absent(),
            Value<int> createdAt = const Value.absent(),
          }) =>
              SyncQueueCompanion.insert(
            id: id,
            operation: operation,
            entityType: entityType,
            entityLocalId: entityLocalId,
            payloadJson: payloadJson,
            attemptCount: attemptCount,
            lastAttemptAt: lastAttemptAt,
            lastError: lastError,
            status: status,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$SyncQueueTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $SyncQueueTable,
    SyncQueueData,
    $$SyncQueueTableFilterComposer,
    $$SyncQueueTableOrderingComposer,
    $$SyncQueueTableAnnotationComposer,
    $$SyncQueueTableCreateCompanionBuilder,
    $$SyncQueueTableUpdateCompanionBuilder,
    (
      SyncQueueData,
      BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>
    ),
    SyncQueueData,
    PrefetchHooks Function()>;
typedef $$AuditLogTableCreateCompanionBuilder = AuditLogCompanion Function({
  Value<int> id,
  required String userId,
  required String operation,
  Value<String?> entityType,
  Value<String?> entityId,
  Value<String?> detailJson,
  Value<int> occurredAt,
});
typedef $$AuditLogTableUpdateCompanionBuilder = AuditLogCompanion Function({
  Value<int> id,
  Value<String> userId,
  Value<String> operation,
  Value<String?> entityType,
  Value<String?> entityId,
  Value<String?> detailJson,
  Value<int> occurredAt,
});

class $$AuditLogTableFilterComposer
    extends Composer<_$AppDatabase, $AuditLogTable> {
  $$AuditLogTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get userId => $composableBuilder(
      column: $table.userId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get operation => $composableBuilder(
      column: $table.operation, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get entityId => $composableBuilder(
      column: $table.entityId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get detailJson => $composableBuilder(
      column: $table.detailJson, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get occurredAt => $composableBuilder(
      column: $table.occurredAt, builder: (column) => ColumnFilters(column));
}

class $$AuditLogTableOrderingComposer
    extends Composer<_$AppDatabase, $AuditLogTable> {
  $$AuditLogTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get userId => $composableBuilder(
      column: $table.userId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get operation => $composableBuilder(
      column: $table.operation, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get entityId => $composableBuilder(
      column: $table.entityId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get detailJson => $composableBuilder(
      column: $table.detailJson, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get occurredAt => $composableBuilder(
      column: $table.occurredAt, builder: (column) => ColumnOrderings(column));
}

class $$AuditLogTableAnnotationComposer
    extends Composer<_$AppDatabase, $AuditLogTable> {
  $$AuditLogTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get userId =>
      $composableBuilder(column: $table.userId, builder: (column) => column);

  GeneratedColumn<String> get operation =>
      $composableBuilder(column: $table.operation, builder: (column) => column);

  GeneratedColumn<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => column);

  GeneratedColumn<String> get entityId =>
      $composableBuilder(column: $table.entityId, builder: (column) => column);

  GeneratedColumn<String> get detailJson => $composableBuilder(
      column: $table.detailJson, builder: (column) => column);

  GeneratedColumn<int> get occurredAt => $composableBuilder(
      column: $table.occurredAt, builder: (column) => column);
}

class $$AuditLogTableTableManager extends RootTableManager<
    _$AppDatabase,
    $AuditLogTable,
    AuditLogData,
    $$AuditLogTableFilterComposer,
    $$AuditLogTableOrderingComposer,
    $$AuditLogTableAnnotationComposer,
    $$AuditLogTableCreateCompanionBuilder,
    $$AuditLogTableUpdateCompanionBuilder,
    (AuditLogData, BaseReferences<_$AppDatabase, $AuditLogTable, AuditLogData>),
    AuditLogData,
    PrefetchHooks Function()> {
  $$AuditLogTableTableManager(_$AppDatabase db, $AuditLogTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$AuditLogTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$AuditLogTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$AuditLogTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> userId = const Value.absent(),
            Value<String> operation = const Value.absent(),
            Value<String?> entityType = const Value.absent(),
            Value<String?> entityId = const Value.absent(),
            Value<String?> detailJson = const Value.absent(),
            Value<int> occurredAt = const Value.absent(),
          }) =>
              AuditLogCompanion(
            id: id,
            userId: userId,
            operation: operation,
            entityType: entityType,
            entityId: entityId,
            detailJson: detailJson,
            occurredAt: occurredAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String userId,
            required String operation,
            Value<String?> entityType = const Value.absent(),
            Value<String?> entityId = const Value.absent(),
            Value<String?> detailJson = const Value.absent(),
            Value<int> occurredAt = const Value.absent(),
          }) =>
              AuditLogCompanion.insert(
            id: id,
            userId: userId,
            operation: operation,
            entityType: entityType,
            entityId: entityId,
            detailJson: detailJson,
            occurredAt: occurredAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$AuditLogTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $AuditLogTable,
    AuditLogData,
    $$AuditLogTableFilterComposer,
    $$AuditLogTableOrderingComposer,
    $$AuditLogTableAnnotationComposer,
    $$AuditLogTableCreateCompanionBuilder,
    $$AuditLogTableUpdateCompanionBuilder,
    (AuditLogData, BaseReferences<_$AppDatabase, $AuditLogTable, AuditLogData>),
    AuditLogData,
    PrefetchHooks Function()>;
typedef $$DeviceSettingsTableCreateCompanionBuilder = DeviceSettingsCompanion
    Function({
  Value<int> id,
  required String key,
  required String value,
});
typedef $$DeviceSettingsTableUpdateCompanionBuilder = DeviceSettingsCompanion
    Function({
  Value<int> id,
  Value<String> key,
  Value<String> value,
});

class $$DeviceSettingsTableFilterComposer
    extends Composer<_$AppDatabase, $DeviceSettingsTable> {
  $$DeviceSettingsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get key => $composableBuilder(
      column: $table.key, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get value => $composableBuilder(
      column: $table.value, builder: (column) => ColumnFilters(column));
}

class $$DeviceSettingsTableOrderingComposer
    extends Composer<_$AppDatabase, $DeviceSettingsTable> {
  $$DeviceSettingsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get key => $composableBuilder(
      column: $table.key, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get value => $composableBuilder(
      column: $table.value, builder: (column) => ColumnOrderings(column));
}

class $$DeviceSettingsTableAnnotationComposer
    extends Composer<_$AppDatabase, $DeviceSettingsTable> {
  $$DeviceSettingsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get key =>
      $composableBuilder(column: $table.key, builder: (column) => column);

  GeneratedColumn<String> get value =>
      $composableBuilder(column: $table.value, builder: (column) => column);
}

class $$DeviceSettingsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $DeviceSettingsTable,
    DeviceSetting,
    $$DeviceSettingsTableFilterComposer,
    $$DeviceSettingsTableOrderingComposer,
    $$DeviceSettingsTableAnnotationComposer,
    $$DeviceSettingsTableCreateCompanionBuilder,
    $$DeviceSettingsTableUpdateCompanionBuilder,
    (
      DeviceSetting,
      BaseReferences<_$AppDatabase, $DeviceSettingsTable, DeviceSetting>
    ),
    DeviceSetting,
    PrefetchHooks Function()> {
  $$DeviceSettingsTableTableManager(
      _$AppDatabase db, $DeviceSettingsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$DeviceSettingsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$DeviceSettingsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$DeviceSettingsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> key = const Value.absent(),
            Value<String> value = const Value.absent(),
          }) =>
              DeviceSettingsCompanion(
            id: id,
            key: key,
            value: value,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String key,
            required String value,
          }) =>
              DeviceSettingsCompanion.insert(
            id: id,
            key: key,
            value: value,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$DeviceSettingsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $DeviceSettingsTable,
    DeviceSetting,
    $$DeviceSettingsTableFilterComposer,
    $$DeviceSettingsTableOrderingComposer,
    $$DeviceSettingsTableAnnotationComposer,
    $$DeviceSettingsTableCreateCompanionBuilder,
    $$DeviceSettingsTableUpdateCompanionBuilder,
    (
      DeviceSetting,
      BaseReferences<_$AppDatabase, $DeviceSettingsTable, DeviceSetting>
    ),
    DeviceSetting,
    PrefetchHooks Function()>;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$SessionsTableTableManager get sessions =>
      $$SessionsTableTableManager(_db, _db.sessions);
  $$DropdownConfigTableTableManager get dropdownConfig =>
      $$DropdownConfigTableTableManager(_db, _db.dropdownConfig);
  $$BoundaryZonesTableTableManager get boundaryZones =>
      $$BoundaryZonesTableTableManager(_db, _db.boundaryZones);
  $$StreetsTableTableManager get streets =>
      $$StreetsTableTableManager(_db, _db.streets);
  $$BuildingsTableTableManager get buildings =>
      $$BuildingsTableTableManager(_db, _db.buildings);
  $$PhotosTableTableManager get photos =>
      $$PhotosTableTableManager(_db, _db.photos);
  $$SyncQueueTableTableManager get syncQueue =>
      $$SyncQueueTableTableManager(_db, _db.syncQueue);
  $$AuditLogTableTableManager get auditLog =>
      $$AuditLogTableTableManager(_db, _db.auditLog);
  $$DeviceSettingsTableTableManager get deviceSettings =>
      $$DeviceSettingsTableTableManager(_db, _db.deviceSettings);
}
