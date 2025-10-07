class BaseWidget {
public:
  virtual ~BaseWidget() = default;
  virtual void render() = 0;
};

class Button : public BaseWidget {
public:
  void render() override;
  void onClick();
};

class Label : public BaseWidget {
public:
  void render() override;
  void setText(const std::string &text);
};

class TextField : public BaseWidget {
public:
  void render() override;
  std::string getText() const;
  void setText(const std::string &text);
};