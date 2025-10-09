#ifndef QVS_HPP
#define QVS_HPP

#include "input.hpp"
#include "numerics.hpp"
#include "qstls.hpp"
#include "vector2D.hpp"
#include "vsbase.hpp"
#include <cmath>
#include <memory>

class QThermoProp;
class QStructProp;
class QstlsCSR;
class QAdder;

// -----------------------------------------------------------------
// Solver for the qVS-STLS scheme
// -----------------------------------------------------------------

class QVSStls : public VSBase, public Qstls {

public:

  // Constructor from initial data
  explicit QVSStls(const std::shared_ptr<const QVSStlsInput> &in_);
  // Solve the scheme
  using VSBase::compute;

private:

  // Thermodyanmic properties
  std::shared_ptr<QThermoProp> thermoProp;
  // Input parameters
  const VSInput &in() const override {
    return *StlsUtil::dynamic_pointer_cast<Input, VSInput>(inPtr);
  }
  // Initialize
  void init() override;
  // Compute free parameter
  double computeAlpha() override;
  // Iterations to solve the qvsstls-scheme
  void updateSolution() override;
  // Print info
  void print(const std::string &msg) { VSBase::print(msg); }
  void println(const std::string &msg) { VSBase::println(msg); }
};

// -----------------------------------------------------------------
// Class to handle the thermodynamic properties
// -----------------------------------------------------------------

class QThermoProp : public ThermoPropBase {

public:

  // Constructors
  explicit QThermoProp(const std::shared_ptr<const QVSStlsInput> &in_);
  // Get internal energy and internal energy derivatives
  std::vector<double> getQData() const;

private:

  std::shared_ptr<QStructProp> structProp;
};

// -----------------------------------------------------------------
// Class to handle the structural properties
// -----------------------------------------------------------------

class QStructProp : public StructPropBase {

public:

  // Constructor
  explicit QStructProp(const std::shared_ptr<const QVSStlsInput> &in_);
  // Get Q term
  std::vector<double> getQ() const;

private:

  // Input parameters
  const QVSStlsInput &in() const {
    return *StlsUtil::dynamic_pointer_cast<IterationInput, QVSStlsInput>(inPtr);
  }
  // Setup dependencies in the CSR objects
  std::vector<QVSStlsInput> setupCSRInput();
  void setupCSR();
};

// -----------------------------------------------------------------
// Class to solve one state point
// -----------------------------------------------------------------

class QstlsCSR : public CSR, public Qstls {

public:

  // Constructor
  explicit QstlsCSR(const std::shared_ptr<const QVSStlsInput> &in_);
  // Compute auxiliary density response
  void computeLfcStls() override;
  void computeLfc() override;
  // Publicly esposed private stls methods
  void init() override;
  void initialGuess() override { Qstls::initialGuess(); }
  void computeSsf() override { Qstls::computeSsf(); }
  double computeError() override { return Qstls::computeError(); }
  void updateSolution() override { Qstls::updateSolution(); }
  // Compute Q
  double getQAdder() const;
  // Getters
  const std::vector<double> &getSsf() const override { return Qstls::getSsf(); }
  const std::vector<double> &getWvg() const override { return Qstls::getWvg(); }
  const Vector2D &getLfc() const override { return Qstls::getLfc(); }

private:

  // Integrator for 2D integrals
  const std::shared_ptr<Integrator2D> itg2D;
  std::vector<double> itgGrid;
  // Input parameters
  const VSInput &inVS() const override {
    return *StlsUtil::dynamic_pointer_cast<Input, VSInput>(inPtr);
  }
  const Input &inRpa() const override {
    return *StlsUtil::dynamic_pointer_cast<Input, Input>(inPtr);
  }
};

// -----------------------------------------------------------------
// Class to handle the Q-adder in the free parameter expression
// -----------------------------------------------------------------

class QAdder {

public:

  // Constructor
  QAdder(const double &Theta_,
         const double &mu_,
         const double &limitMin,
         const double &limitMax,
         const std::vector<double> &itgGrid_,
         std::shared_ptr<Integrator1D> itg1_,
         std::shared_ptr<Integrator2D> itg2_,
         std::shared_ptr<Interpolator1D> interp_)
      : Theta(Theta_),
        mu(mu_),
        limits(limitMin, limitMax),
        itgGrid(itgGrid_),
        itg1(itg1_),
        itg2(itg2_),
        interp(interp_) {}
  // Get Q-adder
  double get() const;

private:

  // Degeneracy parameter
  const double Theta;
  // Chemical potential
  const double mu;
  // Integration limits
  const std::pair<double, double> limits;
  // Grid for 2D integration
  const std::vector<double> &itgGrid;
  // Integrator objects
  const std::shared_ptr<Integrator1D> itg1;
  const std::shared_ptr<Integrator2D> itg2;
  // Interpolator 1D class instance
  const std::shared_ptr<Interpolator1D> interp;

  // SSF interpolation
  double ssf(const double &y) const;
  // Integrands
  double integrandDenominator(const double q) const;
  double integrandNumerator1(const double q) const;
  double integrandNumerator2(const double w) const;
  // Get Integral denominator
  void getIntDenominator(double &res) const;
};

#endif
